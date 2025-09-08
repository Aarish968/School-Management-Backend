from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from base import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    date = Column(DateTime)
    status = Column(String)  # present, absent, late, excused
    recorded_by = Column(Integer, ForeignKey("users.id"))
    notes = Column(Text)
    
    # Relationships
    student = relationship("Student")
    course = relationship("Course")
    recorder = relationship("User")
