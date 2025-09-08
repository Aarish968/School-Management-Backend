from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from crud.course import (
    get_course, get_courses, create_course, update_course, delete_course,
    get_courses_by_teacher, get_active_courses, get_course_with_teacher
)
from schemas.course import Course, CourseCreate, CourseUpdate
from router.deps import get_current_active_user, get_current_superuser

router = APIRouter()


@router.get("/", response_model=List[Course])
def read_courses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve courses.
    """
    courses = get_courses(db, skip=skip, limit=limit)
    return courses


@router.get("/active", response_model=List[Course])
def read_active_courses(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve active courses only.
    """
    courses = get_active_courses(db, skip=skip, limit=limit)
    return courses


@router.post("/", response_model=Course)
def create_course_endpoint(
    *,
    db: Session = Depends(get_db),
    course_in: CourseCreate,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Create new course.
    """
    course = create_course(db, course=course_in)
    return course


@router.get("/{course_id}", response_model=Course)
def read_course_by_id(
    course_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific course by id.
    """
    course = get_course(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found",
        )
    return course


@router.get("/{course_id}/with-teacher")
def read_course_with_teacher(
    course_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific course with teacher information.
    """
    course = get_course_with_teacher(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found",
        )
    return course


@router.put("/{course_id}", response_model=Course)
def update_course_endpoint(
    *,
    db: Session = Depends(get_db),
    course_id: int,
    course_in: CourseUpdate,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Update a course.
    """
    course = get_course(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found",
        )
    course = update_course(db, course_id=course_id, course_update=course_in)
    return course


@router.delete("/{course_id}")
def delete_course_endpoint(
    *,
    db: Session = Depends(get_db),
    course_id: int,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Delete a course.
    """
    course = get_course(db, course_id=course_id)
    if not course:
        raise HTTPException(
            status_code=404,
            detail="Course not found",
        )
    delete_course(db, course_id=course_id)
    return {"message": "Course deleted successfully"}


@router.get("/teacher/{teacher_id}", response_model=List[Course])
def read_courses_by_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve courses by teacher.
    """
    courses = get_courses_by_teacher(db, teacher_id=teacher_id, skip=skip, limit=limit)
    return courses
