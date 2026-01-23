# models/subject.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.base import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # Mathematics, Science, English, etc.
    code = Column(String, unique=True, nullable=False)  # MATH101, SCI102, etc.
    description = Column(String, nullable=True)
    credits = Column(Integer, default=1)  # Credit hours for the subject
    institution_type = Column(String, nullable=False)  # school, college
    class_level = Column(Integer, nullable=True)  # For school: 1-12, For college: 1-4
    department = Column(String, nullable=True)  # For college subjects
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relations
    grades = relationship("Grade", back_populates="subject")
    report_cards = relationship("ReportCard", back_populates="subject")