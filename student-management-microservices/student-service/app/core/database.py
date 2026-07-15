"""
Database configuration.

Responsibilities
----------------
- Create SQLAlchemy engine
- Create session factory
- Define Base model
- Provide database dependency

Each microservice owns its own database.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# ---------------------------------------------------------------------
# Database Engine
# ---------------------------------------------------------------------

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,
    future=True,
)


# ---------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


# ---------------------------------------------------------------------
# Base Model
# ---------------------------------------------------------------------

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    """

    pass


# ---------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency.

    Creates one SQLAlchemy session
    per request.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()