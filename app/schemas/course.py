from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CourseBase(BaseModel):
    code: str
    name: str
    description: str
    credits: int
    max_students: int = 30


class CourseCreate(CourseBase):
    teacher_id: int


class CourseUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    credits: Optional[int] = None
    teacher_id: Optional[int] = None
    max_students: Optional[int] = None
    is_active: Optional[bool] = None


class CourseInDB(CourseBase):
    id: int
    teacher_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Course(CourseInDB):
    pass


class CourseWithTeacher(Course):
    teacher: dict  # Will contain teacher information
