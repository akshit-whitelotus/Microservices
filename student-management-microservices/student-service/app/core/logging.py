"""
Central logging configuration.

Responsibilities
----------------
- Configure application logging once.
- Provide reusable loggers.
- Keep log formatting consistent.
"""

from __future__ import annotations

import logging
import sys

from app.core.config import settings


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)-8s | "
    "%(name)s | "
    "%(message)s"
)


def configure_logging() -> None:
    """
    Configure the root logger.

    This function should be called once
    during application startup.
    """

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=LOG_FORMAT,
        stream=sys.stdout,
        force=True,
    )

    # Third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured logger.
    """

    return logging.getLogger(name)