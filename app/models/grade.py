# models/grade.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.base import Base


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Grade details
    assignment_name = Column(String, nullable=False)  # Test 1, Assignment 2, Final Exam, etc.
    grade_type = Column(String, nullable=False)  # test, assignment, quiz, exam, project
    marks_obtained = Column(Float, nullable=False)
    total_marks = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    letter_grade = Column(String, nullable=True)  # A+, A, B+, B, C, D, F
    
    # Academic period
    academic_year = Column(String, nullable=False)  # 2024-25
    semester = Column(String, nullable=True)  # Fall, Spring, Summer (for college)
    term = Column(String, nullable=True)  # 1st Term, 2nd Term, 3rd Term (for school)
    
    # Additional info
    remarks = Column(Text, nullable=True)
    is_published = Column(Boolean, default=False)  # Whether grade is visible to student
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    student = relationship("User", foreign_keys=[student_id], back_populates="student_grades")
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teacher_grades")
    subject = relationship("Subject", back_populates="grades")