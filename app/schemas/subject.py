# schemas/subject.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class SubjectBase(BaseModel):
    name: str
    code: str
    description: Optional[str] = None
    credits: int = 1
    institution_type: str  # school, college
    class_level: Optional[int] = None
    department: Optional[str] = None

    class Config:
        from_attributes = True


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None
    class_level: Optional[int] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None

    class Config:
        from_attributes = True


class SubjectResponse(SubjectBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True