# schemas/attendance.py
from pydantic import BaseModel
from datetime import datetime


# ------------------ Post -------------------------
class AttendanceCreate(BaseModel):
    teacher_id: int

# ---------------- Name And email user model----------------
class UserBasic(BaseModel):
    full_name: str
    email: str

    class Config:
        orm_mode = True

# ----------------- Get -------------------------
class AttendanceOut(BaseModel):
    id: int
    date: datetime
    status: str
    teacher: UserBasic
    student: UserBasic

    class Config:
        orm_mode = True
