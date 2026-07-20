from __future__ import annotations
from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from shared.auth.constants import ACCESS_TOKEN_TYPE


class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True,extra="forbid",)

    access_token: str = Field(description="JWT access token")
    token_type: str = Field(default=ACCESS_TOKEN_TYPE, description="Token type")


class TokenPayload(BaseModel):

    model_config = ConfigDict(
        extra="ignore",
    )

    sub: str
    role:str
    iss: str
    aud: str
    exp: int
    iat: int