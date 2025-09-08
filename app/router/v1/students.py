from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from crud.student import (
    get_student, get_students, create_student, update_student, delete_student,
    get_students_by_grade, get_student_with_user
)
from schemas.student import Student, StudentCreate, StudentUpdate
from router.deps import get_current_active_user, get_current_superuser

router = APIRouter()


@router.get("/", response_model=List[Student])
def read_students(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve students.
    """
    students = get_students(db, skip=skip, limit=limit)
    return students


@router.post("/", response_model=Student)
def create_student_endpoint(
    *,
    db: Session = Depends(get_db),
    student_in: StudentCreate,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Create new student.
    """
    student = create_student(db, student=student_in)
    return student


@router.get("/{student_id}", response_model=Student)
def read_student_by_id(
    student_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific student by id.
    """
    student = get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )
    return student


@router.get("/{student_id}/with-user")
def read_student_with_user(
    student_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific student with user information.
    """
    student = get_student_with_user(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )
    return student


@router.put("/{student_id}", response_model=Student)
def update_student_endpoint(
    *,
    db: Session = Depends(get_db),
    student_id: int,
    student_in: StudentUpdate,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Update a student.
    """
    student = get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )
    student = update_student(db, student_id=student_id, student_update=student_in)
    return student


@router.delete("/{student_id}")
def delete_student_endpoint(
    *,
    db: Session = Depends(get_db),
    student_id: int,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Delete a student.
    """
    student = get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=404,
            detail="Student not found",
        )
    delete_student(db, student_id=student_id)
    return {"message": "Student deleted successfully"}


@router.get("/grade/{grade_level}", response_model=List[Student])
def read_students_by_grade(
    grade_level: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve students by grade level.
    """
    students = get_students_by_grade(db, grade_level=grade_level, skip=skip, limit=limit)
    return students
