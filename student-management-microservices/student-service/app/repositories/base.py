"""
Generic Base Repository.

Responsibilities
----------------
- Generic CRUD operations
- No business logic
- Reusable across repositories
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository implementation.
    """

    def __init__(
        self,
        model: type[ModelType],
    ) -> None:
        self.model = model

    # ---------------------------------------------------------
    # Get By ID
    # ---------------------------------------------------------

    def get_by_id(
        self,
        db: Session,
        obj_id: Any,
    ) -> ModelType | None:

        stmt = select(self.model).where(
            self.model.id == obj_id
        )

        return db.scalar(stmt)

    # ---------------------------------------------------------
    # List
    # ---------------------------------------------------------

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
    ) -> list[ModelType]:

        stmt = (
            select(self.model)
            .order_by(self.model.id)
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.scalars(stmt).all()
        )

    # ---------------------------------------------------------
    # Count
    # ---------------------------------------------------------

    def count(
        self,
        db: Session,
    ) -> int:

        stmt = (
            select(func.count())
            .select_from(self.model)
        )

        return db.scalar(stmt) or 0

    # ---------------------------------------------------------
    # Create
    # ---------------------------------------------------------

    def create(
        self,
        db: Session,
        *,
        obj_in: dict[str, Any],
    ) -> ModelType:

        db_obj = self.model(**obj_in)

        try:
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)

            return db_obj

        except SQLAlchemyError:
            db.rollback()
            raise

    # ---------------------------------------------------------
    # Update
    # ---------------------------------------------------------

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: dict[str, Any],
    ) -> ModelType:

        try:

            for field, value in obj_in.items():
                setattr(
                    db_obj,
                    field,
                    value,
                )

            db.commit()
            db.refresh(db_obj)

            return db_obj

        except SQLAlchemyError:
            db.rollback()
            raise

    # ---------------------------------------------------------
    # Delete
    # ---------------------------------------------------------

    def delete(
        self,
        db: Session,
        *,
        db_obj: ModelType,
    ) -> None:

        try:
            db.delete(db_obj)
            db.commit()

        except SQLAlchemyError:
            db.rollback()
            raise