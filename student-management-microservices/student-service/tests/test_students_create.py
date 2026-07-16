"""
Student creation API tests.

Responsibilities
----------------
- Test POST /students endpoint.
- Test validation.
- Test duplicate email handling.
"""

from __future__ import annotations



def valid_student_payload():

    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@test.com",
        "course": "Computer Science",
        "enrollment_year": 2025,
    }



# ---------------------------------------------------------
# Create Student Success
# ---------------------------------------------------------

def test_create_student_success(
    authenticated_client,
):

    response = authenticated_client.post(
        "/students",
        json=valid_student_payload(),
    )


    assert response.status_code == 201


    body = response.json()


    assert body["first_name"] == "John"

    assert body["last_name"] == "Doe"

    assert body["email"] == "john.doe@test.com"

    assert body["course"] == "Computer Science"

    assert body["enrollment_year"] == 2025


    assert "id" in body

    assert "created_at" in body

    assert "updated_at" in body



# ---------------------------------------------------------
# Duplicate Email
# ---------------------------------------------------------

def test_create_duplicate_email(
    authenticated_client,
):

    payload = valid_student_payload()


    first_response = authenticated_client.post(
        "/students",
        json=payload,
    )


    assert first_response.status_code == 201



    second_response = authenticated_client.post(
        "/students",
        json=payload,
    )


    assert second_response.status_code == 409


    body = second_response.json()


    assert (
        body["error"]["code"]
        == "CONFLICT"
    )



# ---------------------------------------------------------
# Invalid First Name
# ---------------------------------------------------------

def test_create_student_invalid_name(
    authenticated_client,
):

    payload = valid_student_payload()

    payload["first_name"] = "123"



    response = authenticated_client.post(
        "/students",
        json=payload,
    )


    assert response.status_code == 422



# ---------------------------------------------------------
# Invalid Email
# ---------------------------------------------------------

def test_create_student_invalid_email(
    authenticated_client,
):

    payload = valid_student_payload()

    payload["email"] = "invalid-email"



    response = authenticated_client.post(
        "/students",
        json=payload,
    )


    assert response.status_code == 422



# ---------------------------------------------------------
# Invalid Enrollment Year
# ---------------------------------------------------------

def test_create_student_invalid_year(
    authenticated_client,
):

    payload = valid_student_payload()

    payload["enrollment_year"] = 1900



    response = authenticated_client.post(
        "/students",
        json=payload,
    )


    assert response.status_code == 422



# ---------------------------------------------------------
# Extra Fields Forbidden
# ---------------------------------------------------------

def test_create_student_extra_field(
    authenticated_client,
):

    payload = valid_student_payload()

    payload["unknown_field"] = "test"



    response = authenticated_client.post(
        "/students",
        json=payload,
    )


    assert response.status_code == 422