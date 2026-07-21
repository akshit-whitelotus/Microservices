"""
Authentication dependencies.

Student-service validates JWTs *locally* (same strategy as
document-service) instead of calling auth-service's `/verify` endpoint
on every request. Auth-service remains the sole issuer of tokens and
the two services simply share the same signing secret (see
`app/core/security.py` / `shared.auth.jwt`), so:

- No network round-trip (and no hard runtime dependency on
  auth-service being reachable) for every authenticated request.
- One validation strategy across services instead of a mix of
  "call auth-service" (previously here) and "validate locally"
  (document-service), which made behavior inconsistent and made this
  service unavailable whenever auth-service was slow or down.
"""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.database import get_db
from app.core.security import decode_access_token
from app.schemas.token import TokenPayload
from shared.auth.dependencies import require_roles


security = HTTPBearer(auto_error=True)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    """
    Decode and validate the bearer token locally.

    `decode_access_token` (app/core/security.py) already raises
    `UnauthorizedException` -- handled by the app-wide exception
    handler -- for anything invalid, missing, or expired.
    """

    return decode_access_token(credentials.credentials)


def get_current_user_id(
    payload: TokenPayload = Depends(get_current_user),
) -> int:

    return int(payload.sub)


# Only a "teacher" may create, update, or delete student records.
# (Read access -- viewing the roster / a student's grades -- stays
# open to any authenticated user; see students.py and grades.py.)
require_teacher = require_roles(
    "teacher",
    get_current_user=get_current_user,
)


__all__ = [
    "get_db",
    "get_current_user",
    "get_current_user_id",
    "require_teacher",
]
