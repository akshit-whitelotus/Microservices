from __future__ import annotations
from fastapi import APIRouter,Depends,status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.internal_auth import verify_internal_service
from app.schemas.token import TokenPayload
from app.schemas.grade import BulkUpsertRequest,BulkUpsertResult,GradeResponse
from app.services.grade_service import GradeService

router=APIRouter(tags=["Grades"])
service=GradeService()

# NOTE: open to any authenticated user (same as the student roster this
# is linked from in the frontend), not scoped to "your own grades only".
# Doing that properly needs a Student.user_id -> auth-service user link
# that doesn't exist yet -- tracked as follow-up work, not fixed here.
@router.get("/students/{student_id}/grades",response_model=list[GradeResponse])
def list_student_grades(student_id:int,db:Session=Depends(get_db),_:TokenPayload=Depends(get_current_user)):
    return service.list_students_grades(db=db,student_id=student_id)

@router.post("/internal/v1/grades/bulk-upsert",response_model=BulkUpsertResult,status_code=status.HTTP_200_OK)
def bulk_upsert_grades(request:BulkUpsertRequest,db:Session=Depends(get_db),_:None=Depends(verify_internal_service)):
    return service.bulk_upsert(db=db,items=request.items)

