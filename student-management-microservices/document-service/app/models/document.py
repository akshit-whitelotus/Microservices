from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    Integer,
    JSON,
    String,
)
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from app.core.database import Base


class DocumentStatus(str, Enum):
    """
    Document processing states.
    """

    pending = "pending"

    processing = "processing"

    completed = "completed"

    failed = "failed"



class DocumentMetadata(Base):
    """
    Stores uploaded document information
    and processing results.
    """

    __tablename__ = "documents"


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )


    uploaded_by: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )


    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )


    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )


    content_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )


    status: Mapped[DocumentStatus] = mapped_column(
        SQLEnum(
            DocumentStatus,
            name="document_status",
        ),
        nullable=False,
        default=DocumentStatus.pending,
    )


    result_summary: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )


    error_message: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )


    retry_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )


    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )