"""
Authentication & authorization tests for document-service's HTTP
endpoints.

These go through the real ASGI app (see conftest.py's `client`
fixture) with real, locally-signed JWTs -- exercising the actual
`decode_token` / `require_teacher` dependency chain, not a mocked
stand-in for it.
"""

from __future__ import annotations

import io

import pytest

from tests.conftest import auth_header, make_token


pytestmark = pytest.mark.asyncio


def txt_file(content: bytes = b"Name,Marks\nAlice,90\n"):
    return {
        "file": ("marks.txt", io.BytesIO(content), "text/plain")
    }


# ---------------------------------------------------------
# Upload: authentication
# ---------------------------------------------------------

async def test_upload_without_token_is_rejected(client):

    response = await client.post(
        "/api/v1/documents/marks-upload",
        files=txt_file(),
    )

    assert response.status_code in (401, 403)


async def test_upload_with_garbage_token_is_unauthorized(client):

    response = await client.post(
        "/api/v1/documents/marks-upload",
        headers=auth_header("not-a-real-jwt"),
        files=txt_file(),
    )

    assert response.status_code == 401


async def test_upload_with_token_missing_role_is_unauthorized(client):
    """
    Regression test: a well-signed token with no "role" claim used to
    crash `get_current_user` with an uncaught KeyError (-> 500)
    instead of failing authentication cleanly (see
    app/core/dependencies.py).
    """

    token = make_token(role=None)

    response = await client.post(
        "/api/v1/documents/marks-upload",
        headers=auth_header(token),
        files=txt_file(),
    )

    assert response.status_code == 401


# ---------------------------------------------------------
# Upload: authorization (role)
# ---------------------------------------------------------

async def test_upload_student_role_is_forbidden(client):

    token = make_token(role="student")

    response = await client.post(
        "/api/v1/documents/marks-upload",
        headers=auth_header(token),
        files=txt_file(),
    )

    assert response.status_code == 403


async def test_upload_teacher_role_is_accepted(client):

    token = make_token(role="teacher")

    response = await client.post(
        "/api/v1/documents/marks-upload",
        headers=auth_header(token),
        files=txt_file(),
    )

    assert response.status_code == 202
    body = response.json()
    assert body["status"] == "pending"


# ---------------------------------------------------------
# Upload: content-type validation
# ---------------------------------------------------------

async def test_upload_rejects_disallowed_content_type(client):

    token = make_token(role="teacher")

    response = await client.post(
        "/api/v1/documents/marks-upload",
        headers=auth_header(token),
        files={"file": ("marks.exe", io.BytesIO(b"MZ"), "application/octet-stream")},
    )

    assert response.status_code == 422


# ---------------------------------------------------------
# Get document: ownership check
# ---------------------------------------------------------

async def test_teacher_cannot_read_another_teachers_document(client):

    owner_token = make_token(sub="1", role="teacher")
    other_token = make_token(sub="2", role="teacher")

    upload = await client.post(
        "/api/v1/documents/marks-upload",
        headers=auth_header(owner_token),
        files=txt_file(),
    )
    document_id = upload.json()["id"]

    own_read = await client.get(
        f"/api/v1/documents/{document_id}",
        headers=auth_header(owner_token),
    )
    assert own_read.status_code == 200

    other_read = await client.get(
        f"/api/v1/documents/{document_id}",
        headers=auth_header(other_token),
    )
    assert other_read.status_code == 404
