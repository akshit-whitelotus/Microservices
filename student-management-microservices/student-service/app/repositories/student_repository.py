"""
Student Repository.

Responsibilities
----------------
- Database access for Student entity.
- Entity-specific queries.
- No business rules.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student import Student
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    """
    Repository for Student entity.
    """

    def __init__(self) -> None:
        super().__init__(Student)

    # ---------------------------------------------------------
    # Get By Email
    # ---------------------------------------------------------

    def get_by_email(
        self,
        db: Session,
        email: str,
    ) -> Student | None:
        """
        Return a student by email.
        """

        stmt = (
            select(Student)
            .where(Student.email == email)
        )

        return db.scalar(stmt)

    # ---------------------------------------------------------
    # Exists By Email
    # ---------------------------------------------------------

    def exists_by_email(
        self,
        db: Session,
        email: str,
    ) -> bool:
        """
        Check whether a student email exists.
        """

        return (
            self.get_by_email(
                db=db,
                email=email,
            )
            is not None
        )

    # ---------------------------------------------------------
    # Search By Course
    # ---------------------------------------------------------

    def get_by_course(
        self,
        db: Session,
        course: str,
        *,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Student]:
        """
        Return students enrolled in a course.
        """

        stmt = (
            select(Student)
            .where(Student.course == course)
            .order_by(Student.first_name)
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.scalars(stmt).all()
        )

    # ---------------------------------------------------------
    # Search By Enrollment Year
    # ---------------------------------------------------------

    def get_by_enrollment_year(
        self,
        db: Session,
        year: int,
        *,
        skip: int = 0,
        limit: int = 10,
    ) -> list[Student]:
        """
        Return students for a given enrollment year.
        """

        stmt = (
            select(Student)
            .where(Student.enrollment_year == year)
            .order_by(Student.first_name)
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.scalars(stmt).all()
        )