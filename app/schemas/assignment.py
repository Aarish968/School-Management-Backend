from pydantic import BaseModel, field_serializer, model_serializer
from fastapi import Request
from typing import List, Optional
from datetime import date, time
from app.schemas.user import UserOut


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
    filepath: str

    class Config:
        orm_mode = True

    @model_serializer
    def serialize(self, _):
        base_url = "http://localhost:8000"   # 🔒 Hardcoded
        return {
            "id": self.id,
            "filename": self.filename,
            "filepath": f"{base_url}{self.filepath}"
        }


class AssignmentOut(AssignmentBase):
    id: int
    students: List[UserOut] = []
    attachments: List[AttachmentOut] = []

    class Config:
        orm_mode = True
        from_attributes=True

    @field_serializer("students")
    def serialize_students(self, students):
        """Convert User ORM objects -> list of IDs"""
        return [s.id for s in students]
