# schemas/grade.py
from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class GradeBase(BaseModel):
    student_id: int
    subject_id: int
    assignment_name: str
    grade_type: str  # test, assignment, quiz, exam, project
    marks_obtained: float
    total_marks: float
    academic_year: str
    semester: Optional[str] = None
    term: Optional[str] = None
    remarks: Optional[str] = None

    @validator('marks_obtained')
    def validate_marks_obtained(cls, v, values):
        if 'total_marks' in values and v > values['total_marks']:
            raise ValueError('Marks obtained cannot be greater than total marks')
        if v < 0:
            raise ValueError('Marks obtained cannot be negative')
        return v

    @validator('total_marks')
    def validate_total_marks(cls, v):
        if v <= 0:
            raise ValueError('Total marks must be greater than 0')
        return v

    class Config:
        from_attributes = True


class GradeCreate(GradeBase):
    teacher_id: int


class GradeUpdate(BaseModel):
    assignment_name: Optional[str] = None
    grade_type: Optional[str] = None
    marks_obtained: Optional[float] = None
    total_marks: Optional[float] = None
    remarks: Optional[str] = None
    is_published: Optional[bool] = None

    class Config:
        from_attributes = True


class GradeResponse(GradeBase):
    id: int
    teacher_id: int
    percentage: float
    letter_grade: Optional[str]
    is_published: bool
    created_at: datetime
    updated_at: Optional[datetime]

    # Nested objects
    student_name: Optional[str] = None
    teacher_name: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None

    class Config:
        from_attributes = True


class StudentGradesSummary(BaseModel):
    student_id: int
    student_name: str
    academic_year: str
    semester: Optional[str] = None
    term: Optional[str] = None
    total_subjects: int
    average_percentage: float
    overall_grade: str
    grades: list[GradeResponse]

    class Config:
        from_attributes = True