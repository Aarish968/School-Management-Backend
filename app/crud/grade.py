from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from models import Grade, Student, Course
from schemas.grade import GradeCreate, GradeUpdate


def get_grade(db: Session, grade_id: int) -> Optional[Grade]:
    """Get grade by ID."""
    return db.query(Grade).filter(Grade.id == grade_id).first()


def get_grades(db: Session, skip: int = 0, limit: int = 100) -> List[Grade]:
    """Get list of grades with pagination."""
    return db.query(Grade).offset(skip).limit(limit).all()


def get_grades_by_student(db: Session, student_id: int, skip: int = 0, limit: int = 100) -> List[Grade]:
    """Get grades by student."""
    return db.query(Grade).filter(Grade.student_id == student_id).offset(skip).limit(limit).all()


def get_grades_by_course(db: Session, course_id: int, skip: int = 0, limit: int = 100) -> List[Grade]:
    """Get grades by course."""
    return db.query(Grade).filter(Grade.course_id == course_id).offset(skip).limit(limit).all()


def get_grades_by_student_and_course(db: Session, student_id: int, course_id: int, skip: int = 0, limit: int = 100) -> List[Grade]:
    """Get grades by student and course."""
    return db.query(Grade).filter(
        and_(Grade.student_id == student_id, Grade.course_id == course_id)
    ).offset(skip).limit(limit).all()


def create_grade(db: Session, grade: GradeCreate) -> Grade:
    """Create a new grade."""
    db_grade = Grade(**grade.dict())
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade


def update_grade(db: Session, grade_id: int, grade_update: GradeUpdate) -> Optional[Grade]:
    """Update grade information."""
    db_grade = get_grade(db, grade_id)
    if not db_grade:
        return None
    
    update_data = grade_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_grade, field, value)
    
    db.commit()
    db.refresh(db_grade)
    return db_grade


def delete_grade(db: Session, grade_id: int) -> bool:
    """Delete a grade."""
    db_grade = get_grade(db, grade_id)
    if not db_grade:
        return False
    
    db.delete(db_grade)
    db.commit()
    return True


def get_grade_with_details(db: Session, grade_id: int) -> Optional[dict]:
    """Get grade with student and course information."""
    grade = db.query(Grade).join(Student).join(Course).filter(Grade.id == grade_id).first()
    if not grade:
        return None
    
    return {
        "id": grade.id,
        "student_id": grade.student_id,
        "course_id": grade.course_id,
        "assignment_name": grade.assignment_name,
        "score": grade.score,
        "max_score": grade.max_score,
        "grade_type": grade.grade_type,
        "graded_at": grade.graded_at,
        "student": {
            "id": grade.student.id,
            "student_id": grade.student.student_id,
            "grade_level": grade.student.grade_level,
            "user": {
                "id": grade.student.user.id,
                "full_name": grade.student.user.full_name,
                "email": grade.student.user.email
            }
        },
        "course": {
            "id": grade.course.id,
            "code": grade.course.code,
            "name": grade.course.name,
            "credits": grade.course.credits
        }
    }
