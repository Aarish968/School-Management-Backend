from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from models import Course, Teacher
from schemas.course import CourseCreate, CourseUpdate


def get_course(db: Session, course_id: int) -> Optional[Course]:
    """Get course by ID."""
    return db.query(Course).filter(Course.id == course_id).first()


def get_course_by_code(db: Session, code: str) -> Optional[Course]:
    """Get course by code."""
    return db.query(Course).filter(Course.code == code).first()


def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[Course]:
    """Get list of courses with pagination."""
    return db.query(Course).offset(skip).limit(limit).all()


def get_courses_by_teacher(db: Session, teacher_id: int, skip: int = 0, limit: int = 100) -> List[Course]:
    """Get courses by teacher."""
    return db.query(Course).filter(Course.teacher_id == teacher_id).offset(skip).limit(limit).all()


def get_active_courses(db: Session, skip: int = 0, limit: int = 100) -> List[Course]:
    """Get active courses only."""
    return db.query(Course).filter(Course.is_active == True).offset(skip).limit(limit).all()


def create_course(db: Session, course: CourseCreate) -> Course:
    """Create a new course."""
    db_course = Course(**course.dict())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def update_course(db: Session, course_id: int, course_update: CourseUpdate) -> Optional[Course]:
    """Update course information."""
    db_course = get_course(db, course_id)
    if not db_course:
        return None
    
    update_data = course_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_course, field, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course


def delete_course(db: Session, course_id: int) -> bool:
    """Delete a course."""
    db_course = get_course(db, course_id)
    if not db_course:
        return False
    
    db.delete(db_course)
    db.commit()
    return True


def get_course_with_teacher(db: Session, course_id: int) -> Optional[dict]:
    """Get course with teacher information."""
    course = db.query(Course).join(Teacher).filter(Course.id == course_id).first()
    if not course:
        return None
    
    return {
        "id": course.id,
        "code": course.code,
        "name": course.name,
        "description": course.description,
        "credits": course.credits,
        "max_students": course.max_students,
        "is_active": course.is_active,
        "created_at": course.created_at,
        "teacher": {
            "id": course.teacher.id,
            "teacher_id": course.teacher.teacher_id,
            "department": course.teacher.department,
            "user": {
                "id": course.teacher.user.id,
                "full_name": course.teacher.user.full_name,
                "email": course.teacher.user.email
            }
        }
    }
