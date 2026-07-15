"""
Student listing API tests.

Responsibilities
----------------
- Test GET /students
- Test pagination
- Test page validation
- Test page size validation
- Test total count
"""

from __future__ import annotations



def create_student(
    authenticated_client,
    *,
    first_name: str,
    last_name: str,
    email: str,
    course: str,
    enrollment_year: int,
):

    response = authenticated_client.post(
        "/students",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "course": course,
            "enrollment_year": enrollment_year,
        },
    )

    assert response.status_code == 201

    return response.json()



# ---------------------------------------------------------
# Empty List
# ---------------------------------------------------------

def test_list_students_empty(
    authenticated_client,
):

    response = authenticated_client.get(
        "/students"
    )


    assert response.status_code == 200


    body = response.json()


    assert body["items"] == []

    assert body["total"] == 0

    assert body["page"] == 1

    assert body["page_size"] == 10



# ---------------------------------------------------------
# List Students
# ---------------------------------------------------------

def test_list_students_success(
    authenticated_client,
):

    create_student(
        authenticated_client,
        first_name="John",
        last_name="Doe",
        email="john.list@test.com",
        course="Computer Science",
        enrollment_year=2025,
    )


    create_student(
        authenticated_client,
        first_name="Alice",
        last_name="Smith",
        email="alice.list@test.com",
        course="Physics",
        enrollment_year=2024,
    )


    response = authenticated_client.get(
        "/students"
    )


    assert response.status_code == 200


    body = response.json()


    assert body["total"] == 2

    assert len(body["items"]) == 2

    assert body["page"] == 1

    assert body["page_size"] == 10



# ---------------------------------------------------------
# Pagination
# ---------------------------------------------------------

def test_list_students_pagination(
    authenticated_client,
):

    for index in range(5):

        create_student(
            authenticated_client,
            first_name=f"Student{index}",
            last_name="Test",
            email=f"student{index}@test.com",
            course="Computer Science",
            enrollment_year=2025,
        )



    response = authenticated_client.get(
        "/students?page=1&page_size=2"
    )


    assert response.status_code == 200


    body = response.json()


    assert body["total"] == 5

    assert len(body["items"]) == 2

    assert body["page"] == 1

    assert body["page_size"] == 2



# ---------------------------------------------------------
# Second Page
# ---------------------------------------------------------

def test_list_students_second_page(
    authenticated_client,
):

    for index in range(5):

        create_student(
            authenticated_client,
            first_name=f"Student{index}",
            last_name="Test",
            email=f"page{index}@test.com",
            course="Computer Science",
            enrollment_year=2025,
        )


    response = authenticated_client.get(
        "/students?page=2&page_size=2"
    )


    assert response.status_code == 200


    body = response.json()


    assert body["page"] == 2

    assert len(body["items"]) == 2



# ---------------------------------------------------------
# Invalid Page
# ---------------------------------------------------------

def test_list_students_invalid_page(
    authenticated_client,
):

    response = authenticated_client.get(
        "/students?page=0"
    )


    assert response.status_code == 422



# ---------------------------------------------------------
# Invalid Page Size
# ---------------------------------------------------------

def test_list_students_invalid_page_size(
    authenticated_client,
):

    response = authenticated_client.get(
        "/students?page_size=0"
    )


    assert response.status_code == 422



# ---------------------------------------------------------
# Maximum Page Size
# ---------------------------------------------------------

def test_list_students_max_page_size(
    authenticated_client,
):

    response = authenticated_client.get(
        "/students?page_size=101"
    )


    # Your router currently validates only ge=1.
    # Service validates MAX_PAGE_SIZE.
    # Therefore response depends on exception handler.
    assert response.status_code in {
        400,
        422,
    }