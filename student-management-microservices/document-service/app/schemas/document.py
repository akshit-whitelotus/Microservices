from __future__ import annotations

from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
    field_validator,
)

from app.models.document import DocumentStatus


# ---------------------------------------------------------
# AI Extracted Grade Row
# ---------------------------------------------------------

class ExtractedGradeRow(BaseModel):
    """
    Validated output received from AI.
    
    This model is executed before
    any database operation.
    """

    student_id: int = Field(
        ...,
        gt=0,
    )

    subject: str

    marks: float = Field(
        ...,
        ge=0,
    )

    max_marks: float = Field(
        default=100,
        gt=0,
    )

    exam_term: str


    @field_validator(
        "subject",
        "exam_term",
    )
    @classmethod
    def validate_text(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty"
            )

        return value



# ---------------------------------------------------------
# Upload Response
# ---------------------------------------------------------

class DocumentUploadResult(BaseModel):

    id: int

    status: DocumentStatus



# ---------------------------------------------------------
# Document Response
# ---------------------------------------------------------

class DocumentResponse(BaseModel):

    id: int

    uploaded_by: int

    filename: str

    content_type: str

    status: DocumentStatus

    result_summary: dict | None

    error_message: str | None

    retry_count: int

    created_at: datetime

    updated_at: datetime


    model_config = {
        "from_attributes": True,
    }