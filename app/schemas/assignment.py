from pydantic import BaseModel, field_serializer
from typing import List, Optional
from datetime import date, time
from .user import UserOut


class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: Optional[str] = None
    assigned_teacher_id: int
    due_date: date
    due_time: Optional[time] = None


class AssignmentCreate(AssignmentBase):
    students: List[int] = []

class AttachmentOut(BaseModel):
    id: int
    filename: str

    class Config:
        orm_mode = True


class AssignmentOut(AssignmentBase):
    id: int
    students: List[UserOut] = []  # ✅ student IDs only
    attachments: List[AttachmentOut] = []

    class Config:
        orm_mode = True

    @field_serializer("students")
    def serialize_students(self, students):
        """Convert User ORM objects -> list of IDs"""
        return [s.id for s in students]
