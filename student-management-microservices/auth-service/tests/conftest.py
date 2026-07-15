import pytest_asyncio

from httpx import AsyncClient, ASGITransport

from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.db.database import AsyncSessionLocal
from app.core.dependencies import get_db
from sqlalchemy import text

# ---------------------------------------------------------
# Database setup
# ---------------------------------------------------------

@pytest_asyncio.fixture(autouse=True)
async def clean_database():

    async with AsyncSessionLocal() as session:

        await session.execute(
            text(
                """
                TRUNCATE TABLE users
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
# HTTP Client
# ---------------------------------------------------------

@pytest_asyncio.fixture
async def client(
    override_database,
):

    transport = ASGITransport(
        app=app
    )

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:

        yield client