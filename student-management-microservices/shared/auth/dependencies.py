"""
Shared role-checking dependency.

Every service already has its own `get_current_user` dependency (they
return different types: a `TokenPayload`, an ORM `User`, etc.), so this
module doesn't try to unify authentication itself. It only unifies the
"does this authenticated principal have an allowed role" check, which
was previously either missing entirely (student-service) or duplicated
ad hoc (document-service's `require_teacher`).

Usage in a service's app/core/dependencies.py:

    from shared.auth.dependencies import require_roles
    from app.core.security import get_current_user  # or wherever it lives

    require_teacher = require_roles("teacher", get_current_user=get_current_user)

    @router.post("/students")
    def create_student(..., _: TokenPayload = Depends(require_teacher)):
        ...
"""

from __future__ import annotations

from typing import Callable, Protocol, TypeVar

from fastapi import Depends, HTTPException, status


class _HasRole(Protocol):
    role: str


PrincipalT = TypeVar("PrincipalT", bound=_HasRole)


def require_roles(
    *allowed_roles: str,
    get_current_user: Callable[..., PrincipalT],
) -> Callable[..., PrincipalT]:
    """
    Build a FastAPI dependency that only lets the given roles through.

    `get_current_user` is the service's own authentication dependency;
    it is called first (so a missing/invalid token still yields 401),
    and only then is `.role` checked (yielding 403 for a valid-but-
    disallowed principal).
    """

    if not allowed_roles:
        raise ValueError("require_roles() needs at least one role")

    allowed = set(allowed_roles)

    def _dependency(
        current_user: PrincipalT = Depends(get_current_user),
    ) -> PrincipalT:

        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission to perform this action. "
                    f"Requires one of roles: {', '.join(sorted(allowed))}."
                ),
            )

        return current_user

    return _dependency
