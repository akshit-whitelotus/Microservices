"""
Student exception handler tests.

Responsibilities
----------------
- Test global exception handlers.
- Verify error response structure.
- Verify application exceptions.
"""

from __future__ import annotations

from unittest.mock import patch

from sqlalchemy.exc import IntegrityError



# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

def create_student(
    client,
    email="exception@test.com",
):

    return client.post(
        "/students",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": email,
            "course": "Physics",
            "enrollment_year": 2025,
        },
    )



# ---------------------------------------------------------
# 404 Not Found
# ---------------------------------------------------------

def test_not_found_exception(
    client,
):

    import uuid


    response = client.get(
        f"/students/{uuid.uuid4()}",
    )


    assert response.status_code == 404


    body = response.json()


    assert "error" in body

    assert body["error"]["code"] == "NOT_FOUND"



# ---------------------------------------------------------
# 409 Conflict
# ---------------------------------------------------------

def test_conflict_exception_duplicate_email(
    client,
):

    first = create_student(
        client,
        "duplicate@test.com",
    )


    assert first.status_code == 201



    second = create_student(
        client,
        "duplicate@test.com",
    )


    assert second.status_code == 409


    body = second.json()


    assert body["error"]["code"] == "CONFLICT"



# ---------------------------------------------------------
# 422 Validation Error
# ---------------------------------------------------------

def test_validation_exception(
    client,
):

    response = client.post(
        "/students",
        json={
            "first_name": "A",
            "last_name": "B",
            "email": "wrong-email",
            "course": "",
            "enrollment_year": 1900,
        },
    )


    assert response.status_code == 422


    body = response.json()


    assert body["error"]["code"] == (
        "VALIDATION_ERROR"
    )


    assert (
        body["error"]["message"]
        ==
        "Request validation failed."
    )



# ---------------------------------------------------------
# Extra Fields Validation
# ---------------------------------------------------------

def test_extra_fields_validation(
    client,
):

    response = client.post(
        "/students",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "extra@test.com",
            "course": "Physics",
            "enrollment_year": 2025,
            "age": 20,
        },
    )


    assert response.status_code == 422



# ---------------------------------------------------------
# Database Integrity Handler
# ---------------------------------------------------------

def test_database_integrity_error_handler(
    client,
):

    with patch(
        "app.services.student_service.StudentService.create_student"
    ) as mock_create:


        mock_create.side_effect = IntegrityError(
            statement="INSERT",
            params={},
            orig=Exception(
                "duplicate key"
            ),
        )


        response = client.post(
            "/students",
            json={
                "first_name": "John",
                "last_name": "Doe",
                "email": "db@test.com",
                "course": "Physics",
                "enrollment_year": 2025,
            },
        )


    assert response.status_code == 409


    body = response.json()


    assert (
        body["error"]["code"]
        ==
        "DATABASE_CONFLICT"
    )



# ---------------------------------------------------------
# Generic Exception Handler
# ---------------------------------------------------------

def test_generic_exception_handler(
    client,
):

    with patch(
        "app.services.student_service.StudentService.list_students"
    ) as mock_list:


        mock_list.side_effect = Exception(
            "Unexpected failure"
        )


        response = client.get(
            "/students",
        )


    assert response.status_code == 500


    body = response.json()


    assert (
        body["error"]["code"]
        ==
        "INTERNAL_SERVER_ERROR"
    )



# ---------------------------------------------------------
# Error Response Shape
# ---------------------------------------------------------

def test_error_response_structure(
    client,
):

    import uuid


    response = client.get(
        f"/students/{uuid.uuid4()}",
    )


    body = response.json()


    assert set(
        body.keys()
    ) == {
        "error"
    }


    assert set(
        body["error"].keys()
    ) == {
        "code",
        "message",
        "details",
    }