# crud/report_card.py
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc
from typing import Optional, List
from app.models.report_card import ReportCard
from app.models.user import User
from app.models.subject import Subject
from app.schemas.report_card import ReportCardCreate, ReportCardUpdate


def calculate_gpa(percentage: float) -> float:
    """Calculate GPA based on percentage (4.0 scale)"""
    if percentage >= 90:
        return 4.0
    elif percentage >= 85:
        return 3.7
    elif percentage >= 80:
        return 3.3
    elif percentage >= 75:
        return 3.0
    elif percentage >= 70:
        return 2.7
    elif percentage >= 65:
        return 2.3
    elif percentage >= 60:
        return 2.0
    else:
        return 0.0


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


def create_report_card(db: Session, report_card: ReportCardCreate) -> ReportCard:
    """Create a new report card"""
    # Calculate percentage, letter grade, GPA, and attendance percentage
    percentage = (report_card.total_marks_obtained / report_card.total_marks_possible) * 100
    letter_grade = calculate_letter_grade(percentage)
    grade_points = calculate_gpa(percentage)
    attendance_percentage = (report_card.classes_attended / report_card.total_classes) * 100 if report_card.total_classes > 0 else 0
    
    db_report_card = ReportCard(
        **report_card.model_dump(),
        percentage=percentage,
        letter_grade=letter_grade,
        grade_points=grade_points,
        attendance_percentage=attendance_percentage
    )
    db.add(db_report_card)
    db.commit()
    db.refresh(db_report_card)
    return db_report_card


def get_report_card(db: Session, report_card_id: int) -> Optional[ReportCard]:
    """Get report card by ID with related data"""
    return db.query(ReportCard).options(
        joinedload(ReportCard.student),
        joinedload(ReportCard.teacher),
        joinedload(ReportCard.subject)
    ).filter(ReportCard.id == report_card_id).first()


def get_report_cards(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    student_id: Optional[int] = None,
    teacher_id: Optional[int] = None,
    subject_id: Optional[int] = None,
    academic_year: Optional[str] = None,
    semester: Optional[str] = None,
    term: Optional[str] = None,
    is_published: Optional[bool] = None,
    is_final: Optional[bool] = None
) -> List[ReportCard]:
    """Get report cards with filters"""
    query = db.query(ReportCard).options(
        joinedload(ReportCard.student),
        joinedload(ReportCard.teacher),
        joinedload(ReportCard.subject)
    )
    
    if student_id:
        query = query.filter(ReportCard.student_id == student_id)
    if teacher_id:
        query = query.filter(ReportCard.teacher_id == teacher_id)
    if subject_id:
        query = query.filter(ReportCard.subject_id == subject_id)
    if academic_year:
        query = query.filter(ReportCard.academic_year == academic_year)
    if semester:
        query = query.filter(ReportCard.semester == semester)
    if term:
        query = query.filter(ReportCard.term == term)
    if is_published is not None:
        query = query.filter(ReportCard.is_published == is_published)
    if is_final is not None:
        query = query.filter(ReportCard.is_final == is_final)
    
    return query.order_by(desc(ReportCard.created_at)).offset(skip).limit(limit).all()


def get_student_report_card_summary(
    db: Session,
    student_id: int,
    academic_year: str,
    semester: Optional[str] = None,
    term: Optional[str] = None
) -> dict:
    """Get student's complete report card summary"""
    query = db.query(ReportCard).filter(
        and_(
            ReportCard.student_id == student_id,
            ReportCard.academic_year == academic_year,
            ReportCard.is_published == True
        )
    )
    
    if semester:
        query = query.filter(ReportCard.semester == semester)
    if term:
        query = query.filter(ReportCard.term == term)
    
    report_cards = query.options(
        joinedload(ReportCard.subject),
        joinedload(ReportCard.student)
    ).all()
    
    if not report_cards:
        return None
    
    # Calculate overall statistics
    total_subjects = len(report_cards)
    overall_percentage = sum(rc.percentage for rc in report_cards) / total_subjects
    overall_grade = calculate_letter_grade(overall_percentage)
    overall_gpa = sum(rc.grade_points for rc in report_cards) / total_subjects
    overall_attendance = sum(rc.attendance_percentage for rc in report_cards) / total_subjects
    
    subjects_passed = sum(1 for rc in report_cards if rc.percentage >= 60)
    subjects_failed = total_subjects - subjects_passed
    
    student = report_cards[0].student
    
    return {
        "student_id": student_id,
        "student_name": student.full_name,
        "student_class": student.classes,
        "student_department": student.department,
        "academic_year": academic_year,
        "semester": semester,
        "term": term,
        "total_subjects": total_subjects,
        "overall_percentage": round(overall_percentage, 2),
        "overall_grade": overall_grade,
        "overall_gpa": round(overall_gpa, 2),
        "overall_attendance": round(overall_attendance, 2),
        "subjects_passed": subjects_passed,
        "subjects_failed": subjects_failed,
        "report_cards": report_cards
    }


def get_class_report_summary(
    db: Session,
    class_level: Optional[int] = None,
    department: Optional[str] = None,
    academic_year: str = None,
    semester: Optional[str] = None,
    term: Optional[str] = None,
    institution_type: str = "school"
) -> dict:
    """Get class-wise report summary"""
    # Build user filter based on institution type
    user_query = db.query(User).filter(
        and_(
            User.role == "student",
            User.institution_type == institution_type
        )
    )
    
    if institution_type == "school" and class_level:
        user_query = user_query.filter(User.classes == class_level)
    elif institution_type == "college" and department:
        user_query = user_query.filter(User.department == department)
    
    students = user_query.all()
    student_ids = [s.id for s in students]
    
    if not student_ids:
        return None
    
    # Get report cards for these students
    query = db.query(ReportCard).filter(
        and_(
            ReportCard.student_id.in_(student_ids),
            ReportCard.academic_year == academic_year,
            ReportCard.is_published == True
        )
    )
    
    if semester:
        query = query.filter(ReportCard.semester == semester)
    if term:
        query = query.filter(ReportCard.term == term)
    
    report_cards = query.all()
    
    if not report_cards:
        return None
    
    # Group by student and calculate individual summaries
    student_summaries = []
    student_percentages = []
    
    for student in students:
        student_report_cards = [rc for rc in report_cards if rc.student_id == student.id]
        if student_report_cards:
            avg_percentage = sum(rc.percentage for rc in student_report_cards) / len(student_report_cards)
            student_percentages.append(avg_percentage)
            
            student_summaries.append({
                "student_id": student.id,
                "student_name": student.full_name,
                "average_percentage": round(avg_percentage, 2),
                "total_subjects": len(student_report_cards)
            })
    
    # Calculate class statistics
    if student_percentages:
        average_percentage = sum(student_percentages) / len(student_percentages)
        highest_percentage = max(student_percentages)
        lowest_percentage = min(student_percentages)
    else:
        average_percentage = highest_percentage = lowest_percentage = 0
    
    return {
        "class_level": class_level,
        "department": department,
        "academic_year": academic_year,
        "semester": semester,
        "term": term,
        "total_students": len(student_summaries),
        "average_percentage": round(average_percentage, 2),
        "highest_percentage": round(highest_percentage, 2),
        "lowest_percentage": round(lowest_percentage, 2),
        "students": student_summaries
    }


def update_report_card(db: Session, report_card_id: int, report_card_update: ReportCardUpdate) -> Optional[ReportCard]:
    """Update report card"""
    db_report_card = get_report_card(db, report_card_id)
    if not db_report_card:
        return None
    
    update_data = report_card_update.model_dump(exclude_unset=True)
    
    # Recalculate derived fields if base values are updated
    recalculate = False
    if any(field in update_data for field in ['total_marks_obtained', 'total_marks_possible', 'classes_attended', 'total_classes']):
        recalculate = True
    
    for field, value in update_data.items():
        setattr(db_report_card, field, value)
    
    if recalculate:
        percentage = (db_report_card.total_marks_obtained / db_report_card.total_marks_possible) * 100
        db_report_card.percentage = percentage
        db_report_card.letter_grade = calculate_letter_grade(percentage)
        db_report_card.grade_points = calculate_gpa(percentage)
        db_report_card.attendance_percentage = (db_report_card.classes_attended / db_report_card.total_classes) * 100 if db_report_card.total_classes > 0 else 0
    
    db.commit()
    db.refresh(db_report_card)
    return db_report_card


def delete_report_card(db: Session, report_card_id: int) -> bool:
    """Delete report card"""
    db_report_card = get_report_card(db, report_card_id)
    if not db_report_card:
        return False
    
    db.delete(db_report_card)
    db.commit()
    return True


def publish_report_cards(db: Session, report_card_ids: List[int]) -> List[ReportCard]:
    """Publish multiple report cards"""
    report_cards = db.query(ReportCard).filter(ReportCard.id.in_(report_card_ids)).all()
    
    for report_card in report_cards:
        report_card.is_published = True
    
    db.commit()
    return report_cards