from pydantic import BaseModel


class TokenPayload(BaseModel):

    sub: str

    role: str

    exp: int

    iat: int

    iss: str

    aud: str