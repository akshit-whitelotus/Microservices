"""
Generic Base Repository.

Responsibilities
----------------
- Generic CRUD operations
- No business logic
- Reusable by every repository
"""

from __future__ import annotations

from typing import Any
from typing import Generic
from typing import Type
from typing import TypeVar

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import Base


ModelType = TypeVar(
    "ModelType",
    bound=Base,
)


class BaseRepository(Generic[ModelType]):
    """
    Generic repository for CRUD operations.
    """

    def __init__(
        self,
        model: Type[ModelType],
    ) -> None:

        self.model = model

    # ------------------------------------------------------------------
    # Get by ID
    # ------------------------------------------------------------------

    def get_by_id(
        self,
        db: Session,
        obj_id: Any,
    ) -> ModelType | None:

        stmt = (
            select(self.model)
            .where(self.model.id == obj_id)
        )

        return db.scalar(stmt)

    # ------------------------------------------------------------------
    # List
    # ------------------------------------------------------------------

    def list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
    ) -> list[ModelType]:

        stmt = (
            select(self.model)
            .offset(skip)
            .limit(limit)
        )

        return list(
            db.scalars(stmt).all()
        )

    # ------------------------------------------------------------------
    # Count
    # ------------------------------------------------------------------

    def count(
        self,
        db: Session,
    ) -> int:

        stmt = (
            select(func.count())
            .select_from(self.model)
        )

        return db.scalar(stmt) or 0

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    def create(
        self,
        db: Session,
        *,
        obj_in: dict[str, Any],
    ) -> ModelType:

        db_obj = self.model(
            **obj_in,
        )

        db.add(db_obj)

        db.commit()

        db.refresh(db_obj)

        return db_obj

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: dict[str, Any],
    ) -> ModelType:

        for field, value in obj_in.items():

            setattr(
                db_obj,
                field,
                value,
            )

        db.commit()

        db.refresh(db_obj)

        return db_obj

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete(
        self,
        db: Session,
        *,
        db_obj: ModelType,
    ) -> None:

        db.delete(db_obj)

        db.commit()