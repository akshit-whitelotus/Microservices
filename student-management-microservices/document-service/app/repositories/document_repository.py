from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import (
    DocumentMetadata,
    DocumentStatus,
)


class DocumentRepository:
    """
    Repository for DocumentMetadata entity.
    """


    async def create(self,db: AsyncSession,document: DocumentMetadata,) -> DocumentMetadata:

        db.add(document)
        await db.flush()
        await db.commit()

        await db.refresh(document)

        return document


    async def get_by_id(
        self,
        db: AsyncSession,
        document_id: int,
    ) -> DocumentMetadata | None:

        result = await db.execute(
            select(DocumentMetadata)
            .where(
                DocumentMetadata.id == document_id
            )
        )

        return result.scalar_one_or_none()


    async def list_by_uploader(
        self,
        db: AsyncSession,
        uploaded_by: int,
    ) -> list[DocumentMetadata]:

        result = await db.execute(
            select(DocumentMetadata)
            .where(
                DocumentMetadata.uploaded_by == uploaded_by
            )
            .order_by(
                DocumentMetadata.created_at.desc()
            )
        )

        return result.scalars().all()

    async def update_status(
    self,
    db: AsyncSession,
    document: DocumentMetadata,
    *,
    status: DocumentStatus,
    result_summary: dict | None = None,
    error_message: str | None = None,
) -> DocumentMetadata:

        document.status = status

        if result_summary is not None:
            document.result_summary = result_summary

        if error_message is not None:
            document.error_message = error_message

        await db.commit()
        await db.refresh(document)

        return document

    async def increment_retry(
        self,
        db: AsyncSession,
        document: DocumentMetadata,
    ) -> DocumentMetadata:

        document.retry_count += 1

        await db.commit()
        await db.refresh(document)

        return document