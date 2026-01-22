from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey, Text, DateTime, func, Table
from sqlalchemy.orm import relationship
from app.base import Base


assignment_students = Table(
    "assignment_students",
    Base.metadata,
    Column("assignment_id", Integer, ForeignKey("assignments.id"), primary_key=True),
    Column("student_id", Integer, ForeignKey("users.id"), primary_key=True),
)


class Assignment(Base):
    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String, nullable=True)  # homework | assignment
    assigned_teacher_id = Column(Integer, ForeignKey("users.id"))
    due_date = Column(Date, nullable=False)
    due_time = Column(Time, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    assigned_teacher = relationship("User", foreign_keys=[assigned_teacher_id])
    students = relationship("User", secondary=assignment_students)
    attachments = relationship("Attachment", back_populates="assignment")