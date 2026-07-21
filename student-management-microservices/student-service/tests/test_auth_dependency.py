"""
Student authentication & authorization integration tests.

Responsibilities
----------------
- Test protected student endpoints.
- Test local JWT validation (student-service validates tokens itself
  now -- see app/core/security.py -- instead of calling auth-service's
  /verify endpoint over the network on every request).
- Test role-based access control on the write endpoints.
"""

from __future__ import annotations

from app.core.config import settings
from shared.auth.jwt import create_access_token


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def make_token(*, role: str | None = "teacher", **overrides) -> str:
    """
    Build a real, locally-verifiable JWT the same way auth-service
    would -- signed with the shared secret/issuer/audience.
    """

    kwargs = dict(
        subject="1",
        role=role,
        secret_key=settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
        expires_minutes=30,
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
    )
    kwargs.update(overrides)

    return create_access_token(**kwargs)


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def sample_payload(email: str) -> dict:
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": email,
        "course": "Physics",
        "enrollment_year": 2025,
    }


# ---------------------------------------------------------
# Missing Token
# ---------------------------------------------------------

def test_create_student_without_token(client):

    response = client.post(
        "/students",
        json=sample_payload("auth@test.com"),
    )

    assert response.status_code == 403


# ---------------------------------------------------------
# Malformed / Garbage Token
# ---------------------------------------------------------

def test_create_student_invalid_token(client):

    response = client.post(
        "/students",
        headers=auth_header("this-is-not-a-jwt"),
        json=sample_payload("invalid@test.com"),
    )

    assert response.status_code == 401


# ---------------------------------------------------------
# Token Signed With The Wrong Secret
# ---------------------------------------------------------

def test_create_student_wrong_signature(client):

    bad_token = make_token(secret_key="a-completely-different-secret-key-1234")

    response = client.post(
        "/students",
        headers=auth_header(bad_token),
        json=sample_payload("wrongsig@test.com"),
    )

    assert response.status_code == 401


# ---------------------------------------------------------
# Expired Token
# ---------------------------------------------------------

def test_create_student_expired_token(client):

    expired_token = make_token(expires_minutes=-5)

    response = client.post(
        "/students",
        headers=auth_header(expired_token),
        json=sample_payload("expired@test.com"),
    )

    assert response.status_code == 401


# ---------------------------------------------------------
# Valid Token, Missing "role" Claim
# ---------------------------------------------------------

def test_invalid_auth_payload_missing_role(client):

    token = make_token(role=None)

    response = client.get(
        "/students",
        headers=auth_header(token),
    )

    assert response.status_code == 401


# ---------------------------------------------------------
# Valid Teacher Token
# ---------------------------------------------------------

def test_create_student_with_valid_teacher_token(client):

    token = make_token(role="teacher")

    response = client.post(
        "/students",
        headers=auth_header(token),
        json=sample_payload("valid@test.com"),
    )

    assert response.status_code == 201

    body = response.json()

    assert body["email"] == "valid@test.com"


def test_get_student_with_valid_token(client):

    token = make_token(role="teacher")

    create = client.post(
        "/students",
        headers=auth_header(token),
        json=sample_payload("alex@test.com"),
    )

    student_id = create.json()["id"]

    response = client.get(
        f"/students/{student_id}",
        headers=auth_header(token),
    )

    assert response.status_code == 200


# ---------------------------------------------------------
# Delete Requires A Token At All
# ---------------------------------------------------------

def test_delete_student_without_token(client):

    response = client.delete("/students/1")

    assert response.status_code == 403


# ---------------------------------------------------------
# Access Control: "student" Role Cannot Write
# ---------------------------------------------------------

def test_student_role_cannot_create_student(client):

    token = make_token(role="student")

    response = client.post(
        "/students",
        headers=auth_header(token),
        json=sample_payload("blocked@test.com"),
    )

    assert response.status_code == 403


def test_student_role_cannot_delete_student(client):

    teacher_token = make_token(role="teacher")

    create = client.post(
        "/students",
        headers=auth_header(teacher_token),
        json=sample_payload("todelete@test.com"),
    )

    student_id = create.json()["id"]

    student_token = make_token(role="student")

    response = client.delete(
        f"/students/{student_id}",
        headers=auth_header(student_token),
    )

    assert response.status_code == 403


def test_student_role_cannot_update_student(client):

    teacher_token = make_token(role="teacher")

    create = client.post(
        "/students",
        headers=auth_header(teacher_token),
        json=sample_payload("toupdate@test.com"),
    )

    student_id = create.json()["id"]

    student_token = make_token(role="student")

    response = client.patch(
        f"/students/{student_id}",
        headers=auth_header(student_token),
        json={"course": "Chemistry"},
    )

    assert response.status_code == 403


# ---------------------------------------------------------
# Access Control: "student" Role Can Still Read
# ---------------------------------------------------------

def test_student_role_can_list_students(client):

    teacher_token = make_token(role="teacher")

    client.post(
        "/students",
        headers=auth_header(teacher_token),
        json=sample_payload("readable@test.com"),
    )

    student_token = make_token(role="student")

    response = client.get(
        "/students",
        headers=auth_header(student_token),
    )

    assert response.status_code == 200
