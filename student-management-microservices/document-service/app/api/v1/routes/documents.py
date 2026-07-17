from __future__ import annotations

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    UploadFile,
    status,
    HTTPException,
)

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_teacher

from app.schemas.token import TokenPayload
from app.schemas.document import (
    DocumentResponse,
    DocumentUploadResult,
)

from app.services.document_service import (
    DocumentService,
)


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


service = DocumentService()


ALLOWED_TYPES = {
    "application/pdf",
    "text/plain",
}


# ---------------------------------------------------------
# Upload Marks Document
# ---------------------------------------------------------

@router.post(
    "/marks-upload",
    response_model=DocumentUploadResult,
    status_code=status.HTTP_202_ACCEPTED,
)
async def upload_marks_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(
        require_teacher
    ),
):

    if file.content_type not in ALLOWED_TYPES:

        raise HTTPException(
            status_code=422,
            detail=(
                "Only PDF and TXT files are supported"
            ),
        )


    content = await file.read()


    document = await service.create_upload(
        db=db,
        uploaded_by=int(
            current_user.sub
        ),
        filename=file.filename,
        content_type=file.content_type,
        file_content=content,
    )


    background_tasks.add_task(
        service.process_document,
        document.id,
    )


    return DocumentUploadResult(
        id=document.id,
        status=document.status,
    )



# ---------------------------------------------------------
# Get Document
# ---------------------------------------------------------

@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(
        require_teacher
    ),
):

    return await service.get_document(
        db=db,
        document_id=document_id,
        uploaded_by=int(
            current_user.sub
        ),
    )



# ---------------------------------------------------------
# List My Uploads
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[DocumentResponse],
)
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: TokenPayload = Depends(
        require_teacher
    ),
):

    return await service.list_documents(
        db=db,
        uploaded_by=int(
            current_user.sub
        ),
    )