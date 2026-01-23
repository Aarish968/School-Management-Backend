# models/report_card.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.base import Base


class ReportCard(Base):
    __tablename__ = "report_cards"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Academic period
    academic_year = Column(String, nullable=False)  # 2024-25
    semester = Column(String, nullable=True)  # Fall, Spring, Summer (for college)
    term = Column(String, nullable=True)  # 1st Term, 2nd Term, 3rd Term (for school)
    
    # Consolidated grades
    total_marks_obtained = Column(Float, nullable=False)
    total_marks_possible = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    letter_grade = Column(String, nullable=False)  # A+, A, B+, B, C, D, F
    grade_points = Column(Float, nullable=False)  # GPA points (4.0 scale)
    
    # Attendance
    classes_attended = Column(Integer, default=0)
    total_classes = Column(Integer, default=0)
    attendance_percentage = Column(Float, default=0.0)
    
    # Teacher feedback
    teacher_remarks = Column(Text, nullable=True)
    strengths = Column(Text, nullable=True)
    areas_for_improvement = Column(Text, nullable=True)
    
    # Status
    is_published = Column(Boolean, default=False)
    is_final = Column(Boolean, default=False)  # Final report card for the term/semester
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    student = relationship("User", foreign_keys=[student_id], back_populates="student_report_cards")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teacher_report_cards")
    subject = relationship("Subject", back_populates="report_cards")