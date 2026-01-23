# crud/subject.py
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, List
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate


def create_subject(db: Session, subject: SubjectCreate) -> Subject:
    """Create a new subject"""
    db_subject = Subject(**subject.model_dump())
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    return db_subject


def get_subject(db: Session, subject_id: int) -> Optional[Subject]:
    """Get subject by ID"""
    return db.query(Subject).filter(Subject.id == subject_id).first()


def get_subject_by_code(db: Session, code: str) -> Optional[Subject]:
    """Get subject by code"""
    return db.query(Subject).filter(Subject.code == code).first()


def get_subjects(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    institution_type: Optional[str] = None,
    class_level: Optional[int] = None,
    department: Optional[str] = None,
    is_active: bool = True
) -> List[Subject]:
    """Get subjects with filters"""
    query = db.query(Subject).filter(Subject.is_active == is_active)
    
    if institution_type:
        query = query.filter(Subject.institution_type == institution_type)
    if class_level:
        query = query.filter(Subject.class_level == class_level)
    if department:
        query = query.filter(Subject.department == department)
    
    return query.offset(skip).limit(limit).all()


def update_subject(db: Session, subject_id: int, subject_update: SubjectUpdate) -> Optional[Subject]:
    """Update subject"""
    db_subject = get_subject(db, subject_id)
    if not db_subject:
        return None
    
    update_data = subject_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_subject, field, value)
    
    db.commit()
    db.refresh(db_subject)
    return db_subject


def delete_subject(db: Session, subject_id: int) -> bool:
    """Soft delete subject (set is_active to False)"""
    db_subject = get_subject(db, subject_id)
    if not db_subject:
        return False
    
    db_subject.is_active = False
    db.commit()
    return True