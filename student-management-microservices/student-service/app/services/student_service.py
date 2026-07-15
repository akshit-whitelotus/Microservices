"""
Student Service.

Responsibilities
----------------
- Business logic
- Validation
- Pagination
- Duplicate checks
- CRUD operations

No SQL should exist here.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)
from app.models.student import Student
from app.repositories.student_repository import StudentRepository
from app.schemas.student import (
    StudentCreate,
    StudentListResponse,
    StudentUpdate,
)


class StudentService:
    """
    Business logic for Student entity.
    """

    def __init__(self) -> None:
        self.repository = StudentRepository()

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def create_student(
        self,
        db: Session,
        student: StudentCreate,
    ) -> Student:

        existing = self.repository.get_by_email(
            db=db,
            email=student.email,
        )

        if existing:
            raise ConflictException(
                message="Student email already exists."
            )

        return self.repository.create(
            db=db,
            obj_in=student.model_dump(),
        )

    # ---------------------------------------------------------
    # Get
    # ---------------------------------------------------------

    def get_student(
        self,
        db: Session,
        student_id: UUID,
    ) -> Student:

        student = self.repository.get_by_id(
            db=db,
            obj_id=student_id,
        )

        if student is None:
            raise NotFoundException(
                message="Student not found."
            )

        return student

    # ---------------------------------------------------------
    # List
    # ---------------------------------------------------------

    def list_students(
        self,
        db: Session,
        *,
        page: int = 1,
        page_size: int = settings.DEFAULT_PAGE_SIZE,
    ) -> StudentListResponse:

        if page < 1:
            raise BadRequestException(
                message="Page must be greater than zero."
            )

        if page_size < 1:
            raise BadRequestException(
                message="Page size must be greater than zero."
            )

        if page_size > settings.MAX_PAGE_SIZE:
            raise BadRequestException(
                message=(
                    f"Maximum page size is "
                    f"{settings.MAX_PAGE_SIZE}."
                )
            )

        skip = (page - 1) * page_size

        students = self.repository.list(
            db=db,
            skip=skip,
            limit=page_size,
        )

        total = self.repository.count(db=db)

        return StudentListResponse(
            items=students,
            total=total,
            page=page,
            page_size=page_size,
        )

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update_student(
        self,
        db: Session,
        *,
        student_id: UUID,
        student_update: StudentUpdate,
    ) -> Student:

        student = self.get_student(
            db=db,
            student_id=student_id,
        )

        update_data = student_update.model_dump(
            exclude_unset=True,
        )

        if "email" in update_data:

            existing = self.repository.get_by_email(
                db=db,
                email=update_data["email"],
            )

            if (
                existing
                and existing.id != student.id
            ):
                raise ConflictException(
                    message="Student email already exists."
                )

        return self.repository.update(
            db=db,
            db_obj=student,
            obj_in=update_data,
        )

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete_student(
        self,
        db: Session,
        student_id: UUID,
    ) -> None:

        student = self.get_student(
            db=db,
            student_id=student_id,
        )

        self.repository.delete(
            db=db,
            db_obj=student,
        )