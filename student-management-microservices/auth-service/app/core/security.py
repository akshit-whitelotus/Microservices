from passlib.context import CryptContext

from shared.auth.jwt import (
    create_access_token as create_jwt_token,
    decode_access_token as decode_jwt_token,
)

from app.core.config import settings


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(data: dict) -> str:

    return create_jwt_token(
        subject=str(data["sub"]),
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
    )


def decode_token(token: str) -> dict | None:

    try:
        return decode_jwt_token(
            token=token,
            secret_key=settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
            issuer=settings.JWT_ISSUER,
            audience=settings.JWT_AUDIENCE,
        )

    except Exception:
        return None 