from __future__ import annotations
import re
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator


USERNAME_REGEX = r"^[a-zA-Z0-9_.-]{3,50}$"


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid",str_strip_whitespace=True,)

    username: str = Field(min_length=3,max_length=50,examples=["akshit"],)
    password: str = Field(min_length=8,max_length=128,examples=["Password@123"],)

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        if not re.fullmatch(USERNAME_REGEX, value):
            raise ValueError(
                "Username may contain only letters, numbers, '_', '-', and '.'."
            )

        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not any(c.isupper() for c in value):
            raise ValueError(
                "Password must contain at least one uppercase letter."
            )
        if not any(c.islower() for c in value):
            raise ValueError(
                "Password must contain at least one lowercase letter."
            )
        if not any(c.isdigit() for c in value):
            raise ValueError(
                "Password must contain at least one digit."
            )
        if not any(
            c in "!@#$%^&*()-_=+[]{};:,.<>?/\\|"
            for c in value
        ):
            raise ValueError("Password must contain at least one special character.")
        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid",str_strip_whitespace=True,)
    username: str
    password: str