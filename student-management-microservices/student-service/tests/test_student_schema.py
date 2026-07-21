"""
Student schema tests.

Responsibilities
----------------
- Test Pydantic validation.
- Test request models.
- Test response models.
- No database.
- No HTTP.
"""

from __future__ import annotations


from datetime import datetime, timezone

import pytest
from pydantic import ValidationError


from app.schemas.student import (
    StudentCreate,
    StudentUpdate,
    StudentResponse,
    StudentListResponse,
)



# ---------------------------------------------------------
# StudentCreate Success
# ---------------------------------------------------------

def test_student_create_success():

    student = StudentCreate(
        first_name="john",
        last_name="doe",
        email="john@test.com",
        course="computer science",
        enrollment_year=2025,
    )


    assert student.first_name == "John"

    assert student.last_name == "Doe"

    assert student.email == "john@test.com"

    assert student.enrollment_year == 2025



# ---------------------------------------------------------
# Name With Numbers
# ---------------------------------------------------------

def test_student_name_invalid():

    with pytest.raises(
        ValidationError
    ):

        StudentCreate(
            first_name="John123",
            last_name="Doe",
            email="john@test.com",
            course="Physics",
            enrollment_year=2025,
        )



# ---------------------------------------------------------
# Special Characters In Name
# ---------------------------------------------------------

def test_student_name_special_character():

    with pytest.raises(
        ValidationError
    ):

        StudentCreate(
            first_name="John@",
            last_name="Doe",
            email="john@test.com",
            course="Physics",
            enrollment_year=2025,
        )



# ---------------------------------------------------------
# Email Validation
# ---------------------------------------------------------

def test_invalid_email():

    with pytest.raises(
        ValidationError
    ):

        StudentCreate(
            first_name="John",
            last_name="Doe",
            email="wrong-email",
            course="Physics",
            enrollment_year=2025,
        )



# ---------------------------------------------------------
# First Name Minimum Length
# ---------------------------------------------------------

def test_first_name_too_short():

    with pytest.raises(
        ValidationError
    ):

        StudentCreate(
            first_name="J",
            last_name="Doe",
            email="john@test.com",
            course="Physics",
            enrollment_year=2025,
        )



# ---------------------------------------------------------
# Course Minimum Length
# ---------------------------------------------------------

def test_course_too_short():

    with pytest.raises(
        ValidationError
    ):

        StudentCreate(
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            course="A",
            enrollment_year=2025,
        )



# ---------------------------------------------------------
# Enrollment Year Lower Limit
# ---------------------------------------------------------

def test_enrollment_year_before_2000():

    with pytest.raises(
        ValidationError
    ):

        StudentCreate(
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            course="Physics",
            enrollment_year=1999,
        )



# ---------------------------------------------------------
# Enrollment Year Upper Limit
# ---------------------------------------------------------

def test_enrollment_year_after_2100():

    with pytest.raises(
        ValidationError
    ):

        StudentCreate(
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            course="Physics",
            enrollment_year=2101,
        )



# ---------------------------------------------------------
# Extra Fields Forbidden
# ---------------------------------------------------------

def test_extra_fields_not_allowed():

    with pytest.raises(
        ValidationError
    ):

        StudentCreate(
            first_name="John",
            last_name="Doe",
            email="john@test.com",
            course="Physics",
            enrollment_year=2025,
            age=20,
        )



# ---------------------------------------------------------
# Whitespace Handling
# ---------------------------------------------------------

def test_whitespace_is_removed():

    student = StudentCreate(
        first_name=" John ",
        last_name=" Doe ",
        email="john@test.com",
        course=" Physics ",
        enrollment_year=2025,
    )


    assert student.first_name == "John"

    assert student.last_name == "Doe"



# ---------------------------------------------------------
# Update Partial Success
# ---------------------------------------------------------

def test_student_update_partial():

    update = StudentUpdate(
        course="Mathematics",
    )


    data = update.model_dump(
        exclude_unset=True
    )


    assert data == {
        "course": "Mathematics"
    }



# ---------------------------------------------------------
# Update Empty Allowed
# ---------------------------------------------------------

def test_student_update_empty():

    update = StudentUpdate()


    assert update.model_dump(
        exclude_unset=True
    ) == {}



# ---------------------------------------------------------
# Update Invalid Name
# ---------------------------------------------------------

def test_student_update_invalid_name():

    with pytest.raises(
        ValidationError
    ):

        StudentUpdate(
            first_name="123"
        )



# ---------------------------------------------------------
# Response Model
# ---------------------------------------------------------

def test_student_response_model():

    response = StudentResponse(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@test.com",
        course="Physics",
        enrollment_year=2025,
        created_at=datetime.now(
            timezone.utc
        ),
        updated_at=datetime.now(
            timezone.utc
        ),
    )


    assert response.first_name == "John"

    assert response.course == "Physics"



# ---------------------------------------------------------
# List Response
# ---------------------------------------------------------

def test_student_list_response():

    item = StudentResponse(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@test.com",
        course="Physics",
        enrollment_year=2025,
        created_at=datetime.now(
            timezone.utc
        ),
        updated_at=datetime.now(
            timezone.utc
        ),
    )


    response = StudentListResponse(
        items=[
            item
        ],
        total=1,
        page=1,
        page_size=10,
    )


    assert response.total == 1

    assert len(response.items) == 1