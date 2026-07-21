"""
Student update API tests.

Responsibilities
----------------
- Test PATCH /students/{student_id}
- Test partial updates
- Test duplicate email handling
- Test missing student handling
"""

from __future__ import annotations



def create_student(
    authenticated_client,
    email="john.update@test.com",
):

    response = authenticated_client.post(
        "/students",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": email,
            "course": "Computer Science",
            "enrollment_year": 2025,
        },
    )

    assert response.status_code == 201

    return response.json()



# ---------------------------------------------------------
# Update Student Success
# ---------------------------------------------------------

def test_update_student_success(
    authenticated_client,
):

    student = create_student(
        authenticated_client,
    )


    response = authenticated_client.patch(
        f"/students/{student['id']}",
        json={
            "course": "Mathematics",
        },
    )


    assert response.status_code == 200


    body = response.json()


    assert body["id"] == student["id"]

    assert body["course"] == "Mathematics"

    # unchanged fields

    assert body["first_name"] == "John"

    assert body["email"] == "john.update@test.com"



# ---------------------------------------------------------
# Update Multiple Fields
# ---------------------------------------------------------

def test_update_multiple_fields(
    authenticated_client,
):

    student = create_student(
        authenticated_client,
    )


    response = authenticated_client.patch(
        f"/students/{student['id']}",
        json={
            "first_name": "Robert",
            "last_name": "Miller",
            "course": "Physics",
            "enrollment_year": 2026,
        },
    )


    assert response.status_code == 200


    body = response.json()


    assert body["first_name"] == "Robert"

    assert body["last_name"] == "Miller"

    assert body["course"] == "Physics"

    assert body["enrollment_year"] == 2026



# ---------------------------------------------------------
# Update Email Success
# ---------------------------------------------------------

def test_update_email_success(
    authenticated_client,
):

    student = create_student(
        authenticated_client,
    )


    response = authenticated_client.patch(
        f"/students/{student['id']}",
        json={
            "email": "new.email@test.com",
        },
    )


    assert response.status_code == 200


    body = response.json()


    assert (
        body["email"]
        == "new.email@test.com"
    )



# ---------------------------------------------------------
# Duplicate Email Conflict
# ---------------------------------------------------------

def test_update_duplicate_email(
    authenticated_client,
):

    first = create_student(
        authenticated_client,
        email="first@test.com",
    )


    create_student(
        authenticated_client,
        email="second@test.com",
    )


    response = authenticated_client.patch(
        f"/students/{first['id']}",
        json={
            "email": "second@test.com",
        },
    )


    assert response.status_code == 409


    body = response.json()


    assert (
        body["error"]["code"]
        == "CONFLICT"
    )



# ---------------------------------------------------------
# Student Not Found
# ---------------------------------------------------------

def test_update_missing_student(
    authenticated_client,
):

    response = authenticated_client.patch(
        "/students/999999999",
        json={
            "course": "Physics",
        },
    )


    assert response.status_code == 404



# ---------------------------------------------------------
# Invalid UUID
# ---------------------------------------------------------

def test_update_non_numeric_id(
    authenticated_client,
):

    response = authenticated_client.patch(
        "/students/not-valid-id",
        json={
            "course": "Physics",
        },
    )


    assert response.status_code == 422



# ---------------------------------------------------------
# Invalid Update Data
# ---------------------------------------------------------

def test_update_invalid_course(
    authenticated_client,
):

    student = create_student(
        authenticated_client,
    )


    response = authenticated_client.patch(
        f"/students/{student['id']}",
        json={
            "course": "",
        },
    )


    assert response.status_code == 422



# ---------------------------------------------------------
# Extra Field Forbidden
# ---------------------------------------------------------

def test_update_extra_field(
    authenticated_client,
):

    student = create_student(
        authenticated_client,
    )


    response = authenticated_client.patch(
        f"/students/{student['id']}",
        json={
            "unknown": "value",
        },
    )


    assert response.status_code == 422