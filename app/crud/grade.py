# crud/grade.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from typing import Optional, List
from app.models.grade import Grade
from app.models.user import User
from app.models.subject import Subject
from app.schemas.grade import GradeCreate, GradeUpdate


def calculate_letter_grade(percentage: float) -> str:
    """Calculate letter grade based on percentage"""
    if percentage >= 90:
        return "A+"
    elif percentage >= 85:
        return "A"
    elif percentage >= 80:
        return "B+"
    elif percentage >= 75:
        return "B"
    elif percentage >= 70:
        return "C+"
    elif percentage >= 65:
        return "C"
    elif percentage >= 60:
        return "D"
    else:
        return "F"


def create_grade(db: Session, grade: GradeCreate) -> Grade:
    """Create a new grade"""
    # Calculate percentage and letter grade
    percentage = (grade.marks_obtained / grade.total_marks) * 100
    letter_grade = calculate_letter_grade(percentage)
    
    db_grade = Grade(
        **grade.model_dump(),
        percentage=percentage,
        letter_grade=letter_grade
    )
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    return db_grade


def get_grade(db: Session, grade_id: int) -> Optional[Grade]:
    """Get grade by ID with related data"""
    return db.query(Grade).options(
        joinedload(Grade.student),
        joinedload(Grade.teacher),
        joinedload(Grade.subject)
    ).filter(Grade.id == grade_id).first()


def get_grades(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    academic_year: Optional[str] = None,
    semester: Optional[str] = None,
    term: Optional[str] = None,
    is_published: Optional[bool] = None
) -> List[Grade]:
    """Get grades with filters"""
    query = db.query(Grade).options(
        joinedload(Grade.student),
        joinedload(Grade.teacher),
        joinedload(Grade.subject)
    )
    
    if student_id:
        query = query.filter(Grade.student_id == student_id)
    if teacher_id:
        query = query.filter(Grade.teacher_id == teacher_id)
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    if academic_year:
        query = query.filter(Grade.academic_year == academic_year)
    if semester:
        query = query.filter(Grade.semester == semester)
    if term:
        query = query.filter(Grade.term == term)
    if is_published is not None:
        query = query.filter(Grade.is_published == is_published)
    
    return query.order_by(desc(Grade.created_at)).offset(skip).limit(limit).all()


def get_student_grades_summary(
    db: Session,
    student_id: int,
    academic_year: str,
    semester: Optional[str] = None,
    term: Optional[str] = None
) -> dict:
    """Get student's grades summary for a specific period"""
    query = db.query(Grade).filter(
        and_(
            Grade.student_id == student_id,
            Grade.academic_year == academic_year,
            Grade.is_published == True
        )
    )
    
    if semester:
        query = query.filter(Grade.semester == semester)
    if term:
        query = query.filter(Grade.term == term)
    
    grades = query.options(
        joinedload(Grade.subject),
        joinedload(Grade.student)
    ).all()
    
    if not grades:
        return None
    
    # Calculate summary statistics
    total_subjects = len(set(grade.subject_id for grade in grades))
    average_percentage = sum(grade.percentage for grade in grades) / len(grades)
    overall_grade = calculate_letter_grade(average_percentage)
    
    return {
        "student_id": student_id,
        "student_name": grades[0].student.full_name,
        "academic_year": academic_year,
        "semester": semester,
        "term": term,
        "total_subjects": total_subjects,
        "average_percentage": round(average_percentage, 2),
        "overall_grade": overall_grade,
        "grades": grades
    }


def update_grade(db: Session, grade_id: int, grade_update: GradeUpdate) -> Optional[Grade]:
    """Update grade"""
    db_grade = get_grade(db, grade_id)
    if not db_grade:
        return None
    
    update_data = grade_update.model_dump(exclude_unset=True)
    
    # Recalculate percentage and letter grade if marks are updated
    if 'marks_obtained' in update_data or 'total_marks' in update_data:
        marks_obtained = update_data.get('marks_obtained', db_grade.marks_obtained)
        total_marks = update_data.get('total_marks', db_grade.total_marks)
        percentage = (marks_obtained / total_marks) * 100
        update_data['percentage'] = percentage
        update_data['letter_grade'] = calculate_letter_grade(percentage)
    
    for field, value in update_data.items():
        setattr(db_grade, field, value)
    
    db.commit()
    db.refresh(db_grade)
    return db_grade


def delete_grade(db: Session, grade_id: int) -> bool:
    """Delete grade"""
    db_grade = get_grade(db, grade_id)
    if not db_grade:
        return False
    
    db.delete(db_grade)
    db.commit()
    return True


def publish_grades(db: Session, grade_ids: List[int]) -> List[Grade]:
    """Publish multiple grades"""
    grades = db.query(Grade).filter(Grade.id.in_(grade_ids)).all()
    
    for grade in grades:
        grade.is_published = True
    
    db.commit()
    return grades