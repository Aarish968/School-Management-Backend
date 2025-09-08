from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class StudentBase(BaseModel):
    student_id: str
    grade_level: str
    date_of_birth: datetime
    address: str
    phone: str
    emergency_contact: str


class StudentCreate(StudentBase):
    user_id: int


class StudentUpdate(BaseModel):
    student_id: Optional[str] = None
    grade_level: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    emergency_contact: Optional[str] = None


class StudentInDB(StudentBase):
    id: int
    user_id: int
    enrollment_date: datetime

    class Config:
        from_attributes = True


class Student(StudentInDB):
    pass


class StudentWithUser(Student):
    user: dict  # Will contain user information
