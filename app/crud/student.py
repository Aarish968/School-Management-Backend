from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from models import Student, User
from schemas.student import StudentCreate, StudentUpdate


def get_student(db: Session, student_id: int) -> Optional[Student]:
    """Get student by ID."""
    return db.query(Student).filter(Student.id == student_id).first()


def get_student_by_student_id(db: Session, student_id: str) -> Optional[Student]:
    """Get student by school student ID."""
    return db.query(Student).filter(Student.student_id == student_id).first()


def get_students(db: Session, skip: int = 0, limit: int = 100) -> List[Student]:
    """Get list of students with pagination."""
    return db.query(Student).offset(skip).limit(limit).all()


def get_students_by_grade(db: Session, grade_level: str, skip: int = 0, limit: int = 100) -> List[Student]:
    """Get students by grade level."""
    return db.query(Student).filter(Student.grade_level == grade_level).offset(skip).limit(limit).all()


def create_student(db: Session, student: StudentCreate) -> Student:
    """Create a new student."""
    db_student = Student(**student.dict())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(db: Session, student_id: int, student_update: StudentUpdate) -> Optional[Student]:
    """Update student information."""
    db_student = get_student(db, student_id)
    if not db_student:
        return None
    
    update_data = student_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_student, field, value)
    
    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, student_id: int) -> bool:
    """Delete a student."""
    db_student = get_student(db, student_id)
    if not db_student:
        return False
    
    db.delete(db_student)
    db.commit()
    return True


def get_student_with_user(db: Session, student_id: int) -> Optional[dict]:
    """Get student with user information."""
    student = db.query(Student).join(User).filter(Student.id == student_id).first()
    if not student:
        return None
    
    return {
        "id": student.id,
        "student_id": student.student_id,
        "grade_level": student.grade_level,
        "date_of_birth": student.date_of_birth,
        "address": student.address,
        "phone": student.phone,
        "emergency_contact": student.emergency_contact,
        "enrollment_date": student.enrollment_date,
        "user": {
            "id": student.user.id,
            "email": student.user.email,
            "username": student.user.username,
            "full_name": student.user.full_name,
            "role": student.user.role
        }
    }
