from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from crud.grade import (
    get_grade, get_grades, create_grade, update_grade, delete_grade,
    get_grades_by_student, get_grades_by_course, get_grades_by_student_and_course,
    get_grade_with_details
)
from schemas.grade import Grade, GradeCreate, GradeUpdate
from router.deps import get_current_active_user, get_current_superuser

router = APIRouter()


@router.get("/", response_model=List[Grade])
def read_grades(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve grades.
    """
    grades = get_grades(db, skip=skip, limit=limit)
    return grades


@router.post("/", response_model=Grade)
def create_grade_endpoint(
    *,
    db: Session = Depends(get_db),
    grade_in: GradeCreate,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Create new grade.
    """
    grade = create_grade(db, grade=grade_in)
    return grade


@router.get("/{grade_id}", response_model=Grade)
def read_grade_by_id(
    grade_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific grade by id.
    """
    grade = get_grade(db, grade_id=grade_id)
    if not grade:
        raise HTTPException(
            status_code=404,
            detail="Grade not found",
        )
    return grade


@router.get("/{grade_id}/with-details")
def read_grade_with_details(
    grade_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific grade with student and course details.
    """
    grade = get_grade_with_details(db, grade_id=grade_id)
    if not grade:
        raise HTTPException(
            status_code=404,
            detail="Grade not found",
        )
    return grade


@router.put("/{grade_id}", response_model=Grade)
def update_grade_endpoint(
    *,
    db: Session = Depends(get_db),
    grade_id: int,
    grade_in: GradeUpdate,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Update a grade.
    """
    grade = get_grade(db, grade_id=grade_id)
    if not grade:
        raise HTTPException(
            status_code=404,
            detail="Grade not found",
        )
    grade = update_grade(db, grade_id=grade_id, grade_update=grade_in)
    return grade


@router.delete("/{grade_id}")
def delete_grade_endpoint(
    *,
    db: Session = Depends(get_db),
    grade_id: int,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Delete a grade.
    """
    grade = get_grade(db, grade_id=grade_id)
    if not grade:
        raise HTTPException(
            status_code=404,
            detail="Grade not found",
        )
    delete_grade(db, grade_id=grade_id)
    return {"message": "Grade deleted successfully"}


@router.get("/student/{student_id}", response_model=List[Grade])
def read_grades_by_student(
    student_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve grades by student.
    """
    grades = get_grades_by_student(db, student_id=student_id, skip=skip, limit=limit)
    return grades


@router.get("/course/{course_id}", response_model=List[Grade])
def read_grades_by_course(
    course_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve grades by course.
    """
    grades = get_grades_by_course(db, course_id=course_id, skip=skip, limit=limit)
    return grades


@router.get("/student/{student_id}/course/{course_id}", response_model=List[Grade])
def read_grades_by_student_and_course(
    student_id: int,
    course_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve grades by student and course.
    """
    grades = get_grades_by_student_and_course(
        db, student_id=student_id, course_id=course_id, skip=skip, limit=limit
    )
    return grades
