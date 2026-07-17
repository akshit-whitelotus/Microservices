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
                # Extract text
                # ---------------------------------------------

                text = self.extractor.extract(
                    document.file_path,
                    document.content_type,
                )


                logger.info(
                    "Extracted text",
                    extra={
                        "length": len(text),
                        "preview": text[:300],
                    },
                )


                if not text.strip():
                    raise ValueError(
                        "No readable text found in document"
                    )


                # ---------------------------------------------
                # AI extraction
                # ---------------------------------------------

                ai_rows = await self.ai_client.extract_grades(
                    text
                )


                logger.info(
                    "AI extracted rows",
                    extra={
                        "rows": ai_rows,
                    },
                )


                # ---------------------------------------------
                # Validate AI response
                # ---------------------------------------------

                validated_rows = []

                for row in ai_rows:

                    validated_rows.append(
                        ExtractedGradeRow(
                            **row
                        )
                    )


                grade_items = [

                    {
                        "student_id": row.student_id,
                        "subject": row.subject,
                        "marks": row.marks,
                        "max_marks": row.max_marks,
                        "exam_term": row.exam_term,
                    }

                    for row in validated_rows

                ]


                logger.info(
                    "Sending grades",
                    extra={
                        "items": grade_items,
                    },
                )


                # ---------------------------------------------
                # Student service
                # ---------------------------------------------

                result = await self.student_client.bulk_upsert_grades(
                    items=grade_items,
                    uploaded_by=document.uploaded_by,
                    source_document_id=str(
                        document.id
                    ),
                )


                logger.info(
                    "Student service response",
                    extra={
                        "result": result,
                    },
                )


                summary = {

                    "matched": (
                        result.get(
                            "created",
                            0,
                        )
                        +
                        result.get(
                            "updated",
                            0,
                        )
                    ),

                    "not_found_student_ids":
                        result.get(
                            "not_found_student_ids",
                            [],
                        ),

                    "prompt_version":
                        PROMPT_VERSION,
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


                document = await self.repository.get_by_id(
                    db,
                    document_id,
                )


                if document:

                    await self.repository.update_status(
                        db,
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