"""
Pytest configuration.

Responsibilities
----------------
- Configure test database.
- Create tables.
- Override FastAPI database dependency.
- Provide TestClient.
- Provide isolated database session.
- Mock authentication.
"""

from __future__ import annotations


import os

import pytest

from fastapi.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session


from app.main import app

from app.core.database import Base, get_db

from app.core.dependencies import get_current_user

from app.schemas.token import TokenPayload



# ---------------------------------------------------------
# Test Database
# ---------------------------------------------------------

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/student_service_test_db",
)



engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)



TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)



# ---------------------------------------------------------
# Database Setup
# ---------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def create_test_database():

    Base.metadata.create_all(
        bind=engine
    )


    yield


    Base.metadata.drop_all(
        bind=engine
    )



# ---------------------------------------------------------
# Database Session
# ---------------------------------------------------------

@pytest.fixture
def db_session():

    connection = engine.connect()


    transaction = connection.begin()


    session = TestingSessionLocal(
        bind=connection
    )


    try:

        yield session


    finally:

        session.close()

        transaction.rollback()

        connection.close()



# ---------------------------------------------------------
# Override FastAPI DB Dependency
# ---------------------------------------------------------

@pytest.fixture
def override_database(
    db_session,
):

    def override_get_db():

        yield db_session


    app.dependency_overrides[
        get_db
    ] = override_get_db


    yield


    app.dependency_overrides.clear()



# ---------------------------------------------------------
# Mock Authentication
# ---------------------------------------------------------

@pytest.fixture
def mock_auth():

    async def override_current_user():

        return TokenPayload(
            sub="1",
            iss="auth-service",
            aud="student-service",
            exp=9999999999,
            iat=1000000000,
        )

    app.dependency_overrides[get_current_user] = override_current_user

    yield

    app.dependency_overrides.pop(
        get_current_user,
        None,
    )


# ---------------------------------------------------------
# Normal client (real authentication)
# ---------------------------------------------------------

@pytest.fixture
def client(
    override_database,
):

    with TestClient(
    app,
    raise_server_exceptions=False,
) as client:
        yield client


# ---------------------------------------------------------
# Authenticated client (mock authentication)
# ---------------------------------------------------------

@pytest.fixture
def authenticated_client(
    override_database,
    mock_auth,
):

    with TestClient(
    app,
    raise_server_exceptions=False,
) as client:
        yield client