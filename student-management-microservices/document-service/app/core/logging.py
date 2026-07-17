import logging
import sys
from typing import Final


LOG_FORMAT: Final[str] = (
    "%(asctime)s | %(levelname)s | "
    "%(name)s | %(message)s"
)


def configure_logging() -> None:
    """
    Configure application-wide structured logging.
    """

    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )


def get_logger(name: str) -> logging.Logger:
    """
    Returns module logger.
    """

    return logging.getLogger(name)