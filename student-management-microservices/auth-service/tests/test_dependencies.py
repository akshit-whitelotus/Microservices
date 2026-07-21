import pytest

from app.schemas.token import TokenPayload
from app.core.dependencies import get_token_payload



@pytest.mark.asyncio
async def test_token_payload_structure():


    payload={
        "sub":"1",
        "role": "student" or "teacher",
        "iss":"auth-service",
        "aud":"student-service",
        "exp":123456,
        "iat":123456,
    }


    token_payload=TokenPayload(
        **payload
    )


    assert token_payload.sub=="1"

    assert token_payload.iss=="auth-service"