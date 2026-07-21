"""
Pytest configuration for document-service.

Responsibilities
----------------
- Clean the `documents` table between tests (same TRUNCATE approach
  auth-service uses for `users` -- both services run an async
  SQLAlchemy engine against a real Postgres database, so there's no
  in-memory/sqlite shortcut available here).
- Override the `get_db` dependency so requests use the test session.
- Provide an httpx AsyncClient wired to the app via ASGITransport.
- Provide a helper to mint real, locally-verifiable JWTs (document-
  service validates tokens itself -- see app/core/security.py -- so
  tests exercise the real decode path instead of mocking it away).
- Point UPLOAD_DIR at a per-test temp directory so tests never touch
  (or leave junk behind in) the real ./uploads folder.
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.core.config import settings
from app.core.database import AsyncSessionLocal, get_db
from app.main import app
from shared.auth.jwt import create_access_token


# ---------------------------------------------------------
# Upload directory isolation
# ---------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated_upload_dir(tmp_path, monkeypatch):
    """
    Point UPLOAD_DIR at a throwaway directory for every test so the
    suite never writes into (or reads stale files from) the real
    `document-service/uploads/` folder.
    """

    monkeypatch.setattr(settings, "UPLOAD_DIR", str(tmp_path))

    yield tmp_path


# ---------------------------------------------------------
# Database cleanup
# ---------------------------------------------------------

@pytest_asyncio.fixture(autouse=True)
async def clean_database():

    async with AsyncSessionLocal() as session:

        await session.execute(
            text(
                """
                TRUNCATE TABLE documents
                RESTART IDENTITY
                CASCADE
                """
            )
        )

        await session.commit()

    yield


# ---------------------------------------------------------
# Override get_db
# ---------------------------------------------------------

@pytest_asyncio.fixture
async def override_database():

    async def _override_get_db():

        async with AsyncSessionLocal() as session:

            yield session

    app.dependency_overrides[get_db] = _override_get_db

    yield

    app.dependency_overrides.clear()


# ---------------------------------------------------------
# HTTP client
# ---------------------------------------------------------

@pytest_asyncio.fixture
async def client(override_database):

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        yield client


# ---------------------------------------------------------
# JWT helper
# ---------------------------------------------------------

def make_token(*, sub: str = "1", role: str | None = "teacher", **overrides) -> str:
    """
    Build a real JWT the same way auth-service would -- signed with
    the same shared secret/issuer/audience document-service checks.
    """

    kwargs = dict(
        subject=sub,
        role=role,
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_minutes=30,
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
    )
    kwargs.update(overrides)

    return create_access_token(**kwargs)


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}
