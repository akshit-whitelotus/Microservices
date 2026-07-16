"""
Student repository tests.

Responsibilities
----------------
- Test database access layer.
- Test StudentRepository methods.
- Test BaseRepository CRUD methods.
- No HTTP.
- No business rules.
"""

from __future__ import annotations


import uuid

from app.models.student import Student
from app.repositories.student_repository import (
    StudentRepository,
)



# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------

def create_student(
    db_session,
    *,
    email="repo@test.com",
    course="Computer Science",
    year=2025,
):

    student = Student(
        first_name="John",
        last_name="Doe",
        email=email,
        course=course,
        enrollment_year=year,
    )

    db_session.add(student)

    db_session.commit()

    db_session.refresh(student)

    return student



# ---------------------------------------------------------
# Repository Fixture
# ---------------------------------------------------------

def test_repository_instance():

    repo = StudentRepository()

    assert repo is not None

    assert repo.model == Student



# ---------------------------------------------------------
# Create
# ---------------------------------------------------------

def test_create_student(
    db_session,
):

    repo = StudentRepository()


    student = repo.create(
        db=db_session,
        obj_in={
            "first_name": "John",
            "last_name": "Doe",
            "email": "create@test.com",
            "course": "Physics",
            "enrollment_year": 2025,
        },
    )


    assert student.id is not None

    assert student.email == "create@test.com"



# ---------------------------------------------------------
# Get By ID
# ---------------------------------------------------------

def test_get_by_id(
    db_session,
):

    repo = StudentRepository()


    student = create_student(
        db_session,
    )


    result = repo.get_by_id(
        db=db_session,
        obj_id=student.id,
    )


    assert result is not None

    assert result.id == student.id



# ---------------------------------------------------------
# Missing ID
# ---------------------------------------------------------

def test_get_by_invalid_id(
    db_session,
):

    repo = StudentRepository()


    result = repo.get_by_id(
        db=db_session,
        obj_id=uuid.uuid4(),
    )


    assert result is None



# ---------------------------------------------------------
# List
# ---------------------------------------------------------

def test_list_students(
    db_session,
):

    repo = StudentRepository()


    create_student(
        db_session,
        email="one@test.com",
    )


    create_student(
        db_session,
        email="two@test.com",
    )


    result = repo.list(
        db=db_session,
        skip=0,
        limit=10,
    )


    assert len(result) == 2



# ---------------------------------------------------------
# Pagination
# ---------------------------------------------------------

def test_list_students_pagination(
    db_session,
):

    repo = StudentRepository()


    for index in range(5):

        create_student(
            db_session,
            email=f"{index}@test.com",
        )


    result = repo.list(
        db=db_session,
        skip=0,
        limit=2,
    )


    assert len(result) == 2



# ---------------------------------------------------------
# Count
# ---------------------------------------------------------

def test_count_students(
    db_session,
):

    repo = StudentRepository()


    create_student(
        db_session,
    )


    count = repo.count(
        db=db_session,
    )


    assert count == 1



# ---------------------------------------------------------
# Get By Email
# ---------------------------------------------------------

def test_get_by_email(
    db_session,
):

    repo = StudentRepository()


    student = create_student(
        db_session,
        email="email@test.com",
    )


    result = repo.get_by_email(
        db=db_session,
        email="email@test.com",
    )


    assert result.id == student.id



# ---------------------------------------------------------
# Exists By Email
# ---------------------------------------------------------

def test_exists_by_email(
    db_session,
):

    repo = StudentRepository()


    create_student(
        db_session,
        email="exists@test.com",
    )


    assert repo.exists_by_email(
        db=db_session,
        email="exists@test.com",
    )


    assert not repo.exists_by_email(
        db=db_session,
        email="missing@test.com",
    )



# ---------------------------------------------------------
# Search Course
# ---------------------------------------------------------

def test_get_by_course(
    db_session,
):

    repo = StudentRepository()


    create_student(
        db_session,
        email="cs@test.com",
        course="Computer Science",
    )


    create_student(
        db_session,
        email="physics@test.com",
        course="Physics",
    )


    result = repo.get_by_course(
        db=db_session,
        course="Computer Science",
    )


    assert len(result) == 1

    assert result[0].course == "Computer Science"



# ---------------------------------------------------------
# Search Enrollment Year
# ---------------------------------------------------------

def test_get_by_enrollment_year(
    db_session,
):

    repo = StudentRepository()


    create_student(
        db_session,
        email="2025@test.com",
        year=2025,
    )


    create_student(
        db_session,
        email="2024@test.com",
        year=2024,
    )


    result = repo.get_by_enrollment_year(
        db=db_session,
        year=2025,
    )


    assert len(result) == 1

    assert result[0].enrollment_year == 2025



# ---------------------------------------------------------
# Update
# ---------------------------------------------------------

def test_update_student(
    db_session,
):

    repo = StudentRepository()


    student = create_student(
        db_session,
    )


    updated = repo.update(
        db=db_session,
        db_obj=student,
        obj_in={
            "course": "Mathematics",
        },
    )


    assert updated.course == "Mathematics"



# ---------------------------------------------------------
# Delete
# ---------------------------------------------------------

def test_delete_student(
    db_session,
):

    repo = StudentRepository()


    student = create_student(
        db_session,
    )


    repo.delete(
        db=db_session,
        db_obj=student,
    )


    result = repo.get_by_id(
        db=db_session,
        obj_id=student.id,
    )


    assert result is None