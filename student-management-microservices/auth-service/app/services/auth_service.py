from fastapi import HTTPException, status

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)


class AuthService:

    def __init__(
        self,
        repo: UserRepository,
    ):
        self.repo = repo


    async def register(
        self,
        user: UserCreate,
    ):

        existing = await self.repo.get_by_email(
            user.email
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        role = user.role if user.role in {"teacher", "student"} else "student"

        db_user = User(
            username=user.username,
            email=user.email,
            hashed_password=get_password_hash(
                user.password
            ),
            role=role,
        )

        return await self.repo.create(
            db_user
        )


    async def login(
        self,
        username: str,
        password: str,
    ):

        user = await self.repo.get_by_username(
            username
        )

        if not user:
            return None


        if not verify_password(
            password,
            user.hashed_password,
        ):
            return None


        token = create_access_token(
            {
                "sub": str(user.id),
                "role":user.role
            }
        )


        return token