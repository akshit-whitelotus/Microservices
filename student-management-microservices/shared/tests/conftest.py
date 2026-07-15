import pytest


@pytest.fixture
def jwt_secret():

    return (
        "test-secret-key-that-is-long-enough-for-jwt-testing"
    )


@pytest.fixture
def jwt_algorithm():

    return "HS256"


@pytest.fixture
def jwt_issuer():

    return "auth-service"


@pytest.fixture
def jwt_audience():

    return "student-service"