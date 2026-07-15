from app.models.user import User
from app.core.security import get_password_hash


def create_test_user():

    return User(
        username="testuser",
        email="test@test.com",
        hashed_password=get_password_hash(
            "password123"
        ),
    )