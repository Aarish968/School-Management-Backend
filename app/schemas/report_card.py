# schemas/report_card.py
from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class ReportCardBase(BaseModel):
    student_id: int
    subject_id: int
    academic_year: str
    semester: Optional[str] = None
    term: Optional[str] = None
    total_marks_obtained: float
    total_marks_possible: float
    classes_attended: int = 0
    total_classes: int = 0
    teacher_remarks: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None

    @validator('total_marks_obtained')
    def validate_marks_obtained(cls, v, values):
        if 'total_marks_possible' in values and v > values['total_marks_possible']:
            raise ValueError('Marks obtained cannot be greater than total possible marks')
        if v < 0:
            raise ValueError('Marks obtained cannot be negative')
        return v

    @validator('classes_attended')
    def validate_classes_attended(cls, v, values):
        if 'total_classes' in values and v > values['total_classes']:
            raise ValueError('Classes attended cannot be greater than total classes')
        if v < 0:
            raise ValueError('Classes attended cannot be negative')
        return v

    class Config:
        from_attributes = True


class ReportCardCreate(ReportCardBase):
    teacher_id: int


class ReportCardUpdate(BaseModel):
    total_marks_obtained: Optional[float] = None
    total_marks_possible: Optional[float] = None
    classes_attended: Optional[int] = None
    total_classes: Optional[int] = None
    teacher_remarks: Optional[str] = None
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None
    is_published: Optional[bool] = None
    is_final: Optional[bool] = None

    class Config:
        from_attributes = True


class ReportCardResponse(ReportCardBase):
    id: int
    teacher_id: int
    percentage: float
    letter_grade: str
    grade_points: float
    attendance_percentage: float
    is_published: bool
    is_final: bool
    created_at: datetime
    updated_at: Optional[datetime]

    # Nested objects
    student_name: Optional[str] = None
    teacher_name: Optional[str] = None
    subject_name: Optional[str] = None
    subject_code: Optional[str] = None

    class Config:
        from_attributes = True


class StudentReportCardSummary(BaseModel):
    student_id: int
    student_name: str
    student_class: Optional[int] = None
    student_department: Optional[str] = None
    academic_year: str
    semester: Optional[str] = None
    term: Optional[str] = None
    
    # Overall performance
    total_subjects: int
    overall_percentage: float
    overall_grade: str
    overall_gpa: float
    overall_attendance: float
    
    # Subject-wise report cards
    report_cards: List[ReportCardResponse]
    
    # Summary stats
    subjects_passed: int
    subjects_failed: int
    rank: Optional[int] = None

    class Config:
        from_attributes = True


class ClassReportSummary(BaseModel):
    class_level: Optional[int] = None
    department: Optional[str] = None
    academic_year: str
    semester: Optional[str] = None
    term: Optional[str] = None
    
    total_students: int
    average_percentage: float
    highest_percentage: float
    lowest_percentage: float
    
    students: List[StudentReportCardSummary]

    class Config:
        from_attributes = True