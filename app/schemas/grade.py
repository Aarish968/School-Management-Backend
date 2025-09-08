from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GradeBase(BaseModel):
    student_id: int
    course_id: int
    assignment_name: str
    score: float
    max_score: float
    grade_type: str  # assignment, quiz, exam, final


class GradeCreate(GradeBase):
    pass


class GradeUpdate(BaseModel):
    assignment_name: Optional[str] = None
    score: Optional[float] = None
    max_score: Optional[float] = None
    grade_type: Optional[str] = None


class GradeInDB(GradeBase):
    id: int
    graded_at: datetime

    class Config:
        from_attributes = True


class Grade(GradeInDB):
    pass


class GradeWithDetails(Grade):
    student: dict  # Will contain student information
    course: dict   # Will contain course information
