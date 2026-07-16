"""
Student service tests.

Responsibilities
----------------
- Test StudentService business logic.
- No HTTP layer.
- Test duplicate checks.
- Test pagination rules.
- Test update rules.
- Test delete rules.
"""

from __future__ import annotations

import uuid

import pytest

from app.services.student_service import StudentService

from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
)

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
)



@pytest.fixture
def service():

    return StudentService()



def create_student_schema(
    email="john.service@test.com",
):

    return StudentCreate(
        first_name="John",
        last_name="Doe",
        email=email,
        course="Computer Science",
        enrollment_year=2025,
    )



# ---------------------------------------------------------
# Create Student
# ---------------------------------------------------------

def test_create_student_success(
    service,
    db_session,
):

    student = service.create_student(
        db=db_session,
        student=create_student_schema(),
    )


    assert student.email == "john.service@test.com"

    assert student.first_name == "John"



# ---------------------------------------------------------
# Duplicate Email
# ---------------------------------------------------------

def test_create_student_duplicate_email(
    service,
    db_session,
):

    service.create_student(
        db=db_session,
        student=create_student_schema(),
    )


    with pytest.raises(
        ConflictException
    ):

        service.create_student(
            db=db_session,
            student=create_student_schema(),
        )



# ---------------------------------------------------------
# Get Student
# ---------------------------------------------------------

def test_get_student_success(
    service,
    db_session,
):

    created = service.create_student(
        db=db_session,
        student=create_student_schema(),
    )


    result = service.get_student(
        db=db_session,
        student_id=created.id,
    )


    assert result.id == created.id



# ---------------------------------------------------------
# Student Not Found
# ---------------------------------------------------------

def test_get_student_not_found(
    service,
    db_session,
):

    with pytest.raises(
        NotFoundException
    ):

        service.get_student(
            db=db_session,
            student_id=uuid.uuid4(),
        )



# ---------------------------------------------------------
# List Students
# ---------------------------------------------------------

def test_list_students(
    service,
    db_session,
):

    service.create_student(
        db=db_session,
        student=create_student_schema(
            "one@test.com"
        ),
    )


    service.create_student(
        db=db_session,
        student=create_student_schema(
            "two@test.com"
        ),
    )


    result = service.list_students(
        db=db_session,
        page=1,
        page_size=10,
    )


    assert result.total == 2

    assert len(result.items) == 2

    assert result.page == 1

    assert result.page_size == 10



# ---------------------------------------------------------
# Invalid Page
# ---------------------------------------------------------

def test_list_students_invalid_page(
    service,
    db_session,
):

    with pytest.raises(
        BadRequestException
    ):

        service.list_students(
            db=db_session,
            page=0,
        )



# ---------------------------------------------------------
# Invalid Page Size
# ---------------------------------------------------------

def test_list_students_invalid_page_size(
    service,
    db_session,
):

    with pytest.raises(
        BadRequestException
    ):

        service.list_students(
            db=db_session,
            page_size=0,
        )



# ---------------------------------------------------------
# Maximum Page Size
# ---------------------------------------------------------

def test_list_students_exceed_max_page_size(
    service,
    db_session,
):

    with pytest.raises(
        BadRequestException
    ):

        service.list_students(
            db=db_session,
            page_size=101,
        )



# ---------------------------------------------------------
# Update Student
# ---------------------------------------------------------

def test_update_student_success(
    service,
    db_session,
):

    created = service.create_student(
        db=db_session,
        student=create_student_schema(),
    )


    updated = service.update_student(
        db=db_session,
        student_id=created.id,
        student_update=StudentUpdate(
            course="Physics"
        ),
    )


    assert updated.course == "Physics"



# ---------------------------------------------------------
# Update Email Conflict
# ---------------------------------------------------------

def test_update_duplicate_email(
    service,
    db_session,
):

    first = service.create_student(
        db=db_session,
        student=create_student_schema(
            "first@test.com"
        ),
    )


    service.create_student(
        db=db_session,
        student=create_student_schema(
            "second@test.com"
        ),
    )


    with pytest.raises(
        ConflictException
    ):

        service.update_student(
            db=db_session,
            student_id=first.id,
            student_update=StudentUpdate(
                email="second@test.com"
            ),
        )



# ---------------------------------------------------------
# Delete Student
# ---------------------------------------------------------

def test_delete_student(
    service,
    db_session,
):

    created = service.create_student(
        db=db_session,
        student=create_student_schema(),
    )


    service.delete_student(
        db=db_session,
        student_id=created.id,
    )


    with pytest.raises(
        NotFoundException
    ):

        service.get_student(
            db=db_session,
            student_id=created.id,
        )