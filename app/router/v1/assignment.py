import os
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, time
from models.assignment import Assignment
from models.attachment import Attachment
from models.user import User
from schemas.assignment import AssignmentOut
from db import get_db

UPLOAD_DIR = "uploads/"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/assignments")


@router.post("/upload", response_model=AssignmentOut)
async def create_assignment(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    type: Optional[str] = Form(None),
    assigned_teacher_id: int = Form(...),
    due_date: date = Form(...),   # ✅ parse as date
    due_time: Optional[time] = Form(None),  # ✅ parse as time
    students: List[int] = Form([]),
    attachments: List[UploadFile] = File([]),
    db: Session = Depends(get_db),
):

    assignment = Assignment(
        title=title,
        description=description,
        type=type,
        assigned_teacher_id=assigned_teacher_id,
        due_date=due_date,
        due_time=due_time,
    )

    # Add students
    if students:
        db_students = db.query(User).filter(User.id.in_(students)).all()
        assignment.students.extend(db_students)

    # Save files
    for file in attachments:
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        assignment.attachments.append(
            Attachment(filename=file.filename, filepath=f"/uploads/{file.filename}")
        )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return assignment