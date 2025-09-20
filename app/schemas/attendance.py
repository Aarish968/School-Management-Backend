# schemas/attendance.py
from pydantic import BaseModel
from datetime import datetime

class AttendanceCreate(BaseModel):
    teacher_id: int

class AttendanceOut(BaseModel):
    id: int
    date: datetime
    teacher_id: int
    student_id: int
    status: str

    class Config:
        orm_mode = True
