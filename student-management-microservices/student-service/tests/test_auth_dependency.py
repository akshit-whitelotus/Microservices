"""
Student authentication integration tests.

Responsibilities
----------------
- Test protected student endpoints.
- Test JWT dependency behavior.
- Mock auth-service communication.
- No real auth-service required.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient


from app.main import app
from app.schemas.token import TokenPayload



# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

VALID_PAYLOAD = {
    "sub": "1",
    "iss": "auth-service",
    "aud": "student-service",
    "exp": 9999999999,
    "iat": 1000000000,
}



def auth_header():

    return {
        "Authorization": "Bearer fake-token"
    }



# ---------------------------------------------------------
# Missing Token
# ---------------------------------------------------------

def test_create_student_without_token(
    client,
):

    response = client.post(
        "/students",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "auth@test.com",
            "course": "Physics",
            "enrollment_year": 2025,
        },
    )


    assert response.status_code == 403



# ---------------------------------------------------------
# Invalid Token
# ---------------------------------------------------------

def test_create_student_invalid_token(
    client,
):

    with patch(
        "app.core.dependencies.verify_token",
        new_callable=AsyncMock,
    ) as mock_verify:


        mock_verify.side_effect = Exception(
            "Invalid token"
        )


        response = client.post(
            "/students",
            headers=auth_header(),
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "invalid@test.com",
                "course": "Physics",
                "enrollment_year": 2025,
            },
        )


    assert response.status_code in (
        401,
        500,
    )



# ---------------------------------------------------------
# Auth Service Unavailable
# ---------------------------------------------------------

def test_auth_service_unavailable(
    client,
):

    with patch(
        "app.core.dependencies.verify_token",
        new_callable=AsyncMock,
    ) as mock_verify:


        from fastapi import HTTPException


        mock_verify.side_effect = HTTPException(
            status_code=503,
            detail="Authentication service is unavailable.",
        )


        response = client.post(
            "/students",
            headers=auth_header(),
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "service@test.com",
                "course": "Physics",
                "enrollment_year": 2025,
            },
        )


    assert response.status_code == 503



# ---------------------------------------------------------
# Auth Service Returns Valid User
# ---------------------------------------------------------

def test_create_student_with_valid_token(
    client,
):

    with patch(
        "app.core.dependencies.verify_token",
        new_callable=AsyncMock,
    ) as mock_verify:


        mock_verify.return_value = VALID_PAYLOAD


        response = client.post(
            "/students",
            headers=auth_header(),
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "valid@test.com",
                "course": "Computer Science",
                "enrollment_year": 2025,
            },
        )


    assert response.status_code == 201


    body = response.json()


    assert body["email"] == "valid@test.com"



# ---------------------------------------------------------
# Get Student With Valid Token
# ---------------------------------------------------------

def test_get_student_with_valid_token(
    client,
):

    with patch(
        "app.core.dependencies.verify_token",
        new_callable=AsyncMock,
    ) as mock_verify:


        mock_verify.return_value = VALID_PAYLOAD


        create = client.post(
            "/students",
            headers=auth_header(),
            json={
                "first_name": "Alex",
                "last_name": "Smith",
                "email": "alex@test.com",
                "course": "Math",
                "enrollment_year": 2025,
            },
        )


        student_id = create.json()["id"]


        response = client.get(
            f"/students/{student_id}",
            headers=auth_header(),
        )


    assert response.status_code == 200



# ---------------------------------------------------------
# Delete Requires Token
# ---------------------------------------------------------

def test_delete_student_without_token(
    client,
):

    response = client.delete(
        "/students/00000000-0000-0000-0000-000000000001"
    )


    assert response.status_code == 403



# ---------------------------------------------------------
# Invalid Auth Payload
# ---------------------------------------------------------

def test_invalid_auth_payload(
    client,
):

    with patch(
        "app.core.dependencies.verify_token",
        new_callable=AsyncMock,
    ) as mock_verify:


        mock_verify.return_value = {
            "sub": "1"
        }


        response = client.get(
            "/students",
            headers=auth_header(),
        )


    assert response.status_code == 401