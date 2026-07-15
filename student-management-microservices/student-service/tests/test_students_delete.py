"""
Student delete API tests.

Responsibilities
----------------
- Test DELETE /students/{student_id}
- Test successful deletion
- Test missing student deletion
- Verify deleted resource is removed
"""

from __future__ import annotations



def create_student(
    authenticated_client,
):

    response = authenticated_client.post(
        "/students",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.delete@test.com",
            "course": "Computer Science",
            "enrollment_year": 2025,
        },
    )


    assert response.status_code == 201


    return response.json()



# ---------------------------------------------------------
# Delete Success
# ---------------------------------------------------------

def test_delete_student_success(
    authenticated_client,
):

    student = create_student(
        authenticated_client,
    )


    response = authenticated_client.delete(
        f"/students/{student['id']}"
    )


    assert response.status_code == 204


    assert response.content == b""



# ---------------------------------------------------------
# Verify Deleted Student
# ---------------------------------------------------------

def test_deleted_student_not_found(
    authenticated_client,
):

    student = create_student(
        authenticated_client,
    )


    delete_response = authenticated_client.delete(
        f"/students/{student['id']}"
    )


    assert delete_response.status_code == 204



    get_response = authenticated_client.get(
        f"/students/{student['id']}"
    )


    assert get_response.status_code == 404



# ---------------------------------------------------------
# Delete Missing Student
# ---------------------------------------------------------

def test_delete_missing_student(
    authenticated_client,
):

    import uuid


    response = authenticated_client.delete(
        f"/students/{uuid.uuid4()}"
    )


    assert response.status_code == 404


    body = response.json()


    assert (
        body["error"]["code"]
        == "NOT_FOUND"
    )



# ---------------------------------------------------------
# Invalid UUID
# ---------------------------------------------------------

def test_delete_invalid_uuid(
    authenticated_client,
):

    response = authenticated_client.delete(
        "/students/not-a-valid-uuid"
    )


    assert response.status_code == 422