# routers/attendance.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from models.attendance import Attendance
from schemas.attendance import AttendanceCreate, AttendanceOut
from datetime import datetime
from typing import List
from router.deps import get_current_active_user

router = APIRouter(prefix="/attendance", tags=["attendance"])

# ---------------------------✅ POST ------------------------
@router.post("/", response_model=AttendanceOut)
def create_attendance(
    data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)  # returns user object
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    record = Attendance(
        teacher_id=data.teacher_id,
        student_id=current_user.id,  # take from logged-in user
        date=datetime.utcnow(),
        status="pending"
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

# ------------------------ ✅ PUT ------------------------
@router.put("/{attendance_id}/accept", response_model=AttendanceOut)
def accept_attendance(
    attendance_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_active_user)
):  
    print("Current user--------------", current_user.__dict__)
    att = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not att:
        raise HTTPException(status_code=404, detail="Attendance not found")
    if att.teacher_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your request")
    if status not in ["present", "absent"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    att.status = status
    db.commit()
    db.refresh(att)
    return att

# -------------------------------✅ GET Attendance ---------------------------------
# routers/attendance.py
@router.get("/", response_model=List[AttendanceOut])
def get_attendance(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user)
):
    print("Current user--------------", current_user.__dict__)
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    query = db.query(Attendance)

    if current_user.role == "student":
        records = query.filter(Attendance.student_id == current_user.id).all()
    elif current_user.role == "teacher":
        records = query.filter(Attendance.teacher_id == current_user.id).all()
    else:
        raise HTTPException(status_code=403, detail="Not allowed")

    return records

