from sqlalchemy import text

from app.core.database import engine


def test_health_check(client):
    """
    Verify health endpoint returns service status
    and database connectivity.
    """

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "service" in data
    assert "version" in data


def test_database_connection():
    """
    Verify database engine can execute SQL.
    """

    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT 1")
        )

        assert result.scalar() == 1