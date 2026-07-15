"""
Student routes.

Responsibilities
----------------
- Define HTTP endpoints.
- Inject dependencies.
- Delegate business logic to StudentService.
- No business logic should exist here.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.schemas.token import TokenPayload
from app.schemas.student import (
    StudentCreate,
    StudentListResponse,
    StudentResponse,
    StudentUpdate,
)
from app.services.student_service import StudentService


router = APIRouter(
    prefix="/students",
    tags=["Students"],
)

service = StudentService()

@router.post("",response_model=StudentResponse,status_code=status.HTTP_201_CREATED,)
def create_student(student: StudentCreate,db: Session = Depends(get_db),_: TokenPayload = Depends(get_current_user),):
    return service.create_student( db=db,student=student,)
@router.get("/{student_id}",response_model=StudentResponse,)
def get_student(student_id: UUID,db: Session = Depends(get_db),_: TokenPayload = Depends(get_current_user),):
    return service.get_student(db=db,student_id=student_id,)
@router.get("", response_model=StudentListResponse,)
def list_students(page: int = Query(1, ge=1),page_size: int = Query(10, ge=1),db: Session = Depends(get_db), _: TokenPayload = Depends(get_current_user),):
    return service.list_students(db=db,page=page,page_size=page_size,)
@router.patch("/{student_id}",response_model=StudentResponse,)
def update_student(student_id: UUID,student: StudentUpdate,db: Session = Depends(get_db),_: TokenPayload = Depends(get_current_user),):
    return service.update_student(db=db,student_id=student_id,student_update=student,)
@router.delete("/{student_id}",status_code=status.HTTP_204_NO_CONTENT,)
def delete_student(student_id: UUID,db: Session = Depends(get_db),_: TokenPayload = Depends(get_current_user),):
    service.delete_student(db=db,student_id=student_id,)
    return Response(status_code=status.HTTP_204_NO_CONTENT)