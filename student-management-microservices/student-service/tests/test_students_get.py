"""
Student retrieval API tests.

Responsibilities
----------------
- Test GET /students/{student_id}
- Test successful retrieval
- Test missing student handling
- Test invalid UUID handling
"""

from __future__ import annotations



def create_student(
    authenticated_client,
):
    """
    Helper function.

    Creates a student using the real API flow.
    """

    response = authenticated_client.post(
        "/students",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.get@test.com",
            "course": "Computer Science",
            "enrollment_year": 2025,
        },
    )

    assert response.status_code == 201

    return response.json()



# ---------------------------------------------------------
# Get Existing Student
# ---------------------------------------------------------

def test_get_student_success(
    authenticated_client,
):

    student = create_student(
        authenticated_client,
    )


    response = authenticated_client.get(
        f"/students/{student['id']}"
    )


    assert response.status_code == 200


    body = response.json()


    assert body["id"] == student["id"]

    assert body["first_name"] == "John"

    assert body["last_name"] == "Doe"

    assert body["email"] == "john.get@test.com"



# ---------------------------------------------------------
# Get Student Not Found
# ---------------------------------------------------------

def test_get_student_not_found(
    authenticated_client,
):

    response = authenticated_client.get(
        "/students/999999999"
    )


    assert response.status_code == 404


    body = response.json()


    assert (
        body["error"]["code"]
        == "NOT_FOUND"
    )



# ---------------------------------------------------------
# Non-Numeric ID
# ---------------------------------------------------------

def test_get_student_non_numeric_id(
    authenticated_client,
):

    response = authenticated_client.get(
        "/students/not-a-uuid"
    )


    assert response.status_code == 422



# ---------------------------------------------------------
# Multiple Students Isolation
# ---------------------------------------------------------

def test_get_correct_student(
    authenticated_client,
):

    first = authenticated_client.post(
        "/students",
        json={
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@test.com",
            "course": "Physics",
            "enrollment_year": 2024,
        },
    ).json()


    second = authenticated_client.post(
        "/students",
        json={
            "first_name": "Bob",
            "last_name": "Brown",
            "email": "bob@test.com",
            "course": "Math",
            "enrollment_year": 2025,
        },
    ).json()



    response = authenticated_client.get(
        f"/students/{second['id']}"
    )


    assert response.status_code == 200


    body = response.json()


    assert body["id"] == second["id"]

    assert body["id"] != first["id"]    