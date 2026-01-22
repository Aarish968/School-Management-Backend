# models/attendance.py
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.base import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, default="pending")  # pending, present, absent

    # Relations
    teacher = relationship("User", foreign_keys=[teacher_id], back_populates="teacher_attendances")
    student = relationship("User", foreign_keys=[student_id], back_populates="student_attendances")
