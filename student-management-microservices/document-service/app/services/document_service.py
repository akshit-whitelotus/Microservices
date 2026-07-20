from __future__ import annotations

import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.models.document import (
    DocumentMetadata,
    DocumentStatus,
)
from app.repositories.document_repository import (
    DocumentRepository,
)
from app.schemas.document import (
    ExtractedGradeRow,
)
from app.services.text_extractor import (
    TextExtractor,
)
from app.services.ai_client import (
    AIClient,
)
from app.clients.student_client import (
    StudentServiceClient,
)


logger = logging.getLogger(__name__)


PROMPT_VERSION = "v1"


class DocumentService:
    """
    Business logic for document processing.
    """


    def __init__(self) -> None:

        self.repository = (
            DocumentRepository()
        )

        self.extractor = (
            TextExtractor()
        )

        self.ai_client = (
            AIClient()
        )

        self.student_client = (
            StudentServiceClient()
        )


    # ---------------------------------------------------------
    # Upload Document
    # ---------------------------------------------------------

    async def create_upload(
        self,
        db: AsyncSession,
        *,
        uploaded_by: int,
        filename: str,
        content_type: str,
        file_content: bytes,
    ) -> DocumentMetadata:
        """
        Save file and create pending record.
        """

        upload_dir = Path(
            settings.UPLOAD_DIR
        )

        upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = (
            upload_dir / filename
        )

        file_path.write_bytes(
            file_content
        )

        document = DocumentMetadata(
            uploaded_by=uploaded_by,
            filename=filename,
            file_path=str(file_path),
            content_type=content_type,
            status=DocumentStatus.pending,
        )

        return await self.repository.create(
            db,
            document,
        )


    # ---------------------------------------------------------
    # Process Document
    # ---------------------------------------------------------
    async def process_document(
    self,
    document_id: int,
) -> None:

        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:

            try:

                document = await self.repository.get_by_id(
                    db,
                    document_id,
                )

                if document is None:
                    logger.error(
                        "Document not found",
                        extra={
                            "document_id": document_id,
                        },
                    )
                    return


                await self.repository.update_status(
                    db,
                    document,
                    status=DocumentStatus.processing,
                )


                # ---------------------------------------------
                # 1. Extract raw text from the stored file
                # ---------------------------------------------
                text = self.extractor.extract(
                    document.file_path,
                    document.content_type,
                )

                # ---------------------------------------------
                # 2. Ask the AI to pull marks rows out of it
                # ---------------------------------------------
                raw_rows = await self.ai_client.extract_grades(
                    text
                )

                # Validate/coerce each row before sending anything
                # downstream -- drop rows that don't match the shape
                # instead of failing the whole document.
                valid_rows: list[ExtractedGradeRow] = []
                for raw_row in raw_rows:
                    try:
                        valid_rows.append(
                            ExtractedGradeRow(**raw_row)
                        )
                    except Exception:
                        logger.warning(
                            "Skipping malformed row from AI output",
                            extra={
                                "document_id": document_id,
                                "row": raw_row,
                            },
                        )

                if not valid_rows:
                    raise ValueError(
                        "No valid grade rows were extracted from the document"
                    )

                # ---------------------------------------------
                # 3. Push the parsed rows into student-service
                # ---------------------------------------------
                upsert_result = await self.student_client.bulk_upsert_grades(
                    items=[row.model_dump() for row in valid_rows],
                    uploaded_by=document.uploaded_by,
                    source_document_id=str(document.id),
                )

                summary = {
                    "matched": upsert_result.get("created", 0)
                    + upsert_result.get("updated", 0),
                    "created": upsert_result.get("created", 0),
                    "updated": upsert_result.get("updated", 0),
                    "not_found_student_ids": upsert_result.get(
                        "not_found_student_ids", []
                    ),
                    "prompt_version": PROMPT_VERSION,
                }


                await self.repository.update_status(
                    db,
                    document,
                    status=DocumentStatus.completed,
                    result_summary=summary,
                )


            except Exception as exc:

                logger.exception(
                    "Document processing failed",
                    extra={
                        "document_id": document_id,
                        "error": str(exc),
                    },
                )


                async with AsyncSessionLocal() as error_db:

                    document = await self.repository.get_by_id(
                        error_db,
                        document_id,
                    )


                    if document:

                        await self.repository.update_status(
                            error_db,
                            document,
                            status=DocumentStatus.failed,
                            error_message=str(exc),
                        )
    # ---------------------------------------------------------
    # Get Document
    # ---------------------------------------------------------

    async def get_document(
        self,
        db: AsyncSession,
        *,
        document_id: int,
        uploaded_by: int,
    ) -> DocumentMetadata:
        """
        Return document owned by teacher.
        """

        document = await (
            self.repository.get_by_id(
                db,
                document_id,
            )
        )


        if (
            document is None
            or document.uploaded_by != uploaded_by
        ):

            from fastapi import HTTPException


            raise HTTPException(
                status_code=404,
                detail="Document not found",
            )


        return document


    # ---------------------------------------------------------
    # List Documents
    # ---------------------------------------------------------

    async def list_documents(
        self,
        db: AsyncSession,
        *,
        uploaded_by: int,
    ) -> list[DocumentMetadata]:
        """
        Return teacher uploaded documents.
        """

        return  (
             await self.repository.list_by_uploader(
                db,
                uploaded_by,
            )
        )