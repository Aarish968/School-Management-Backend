import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, Request, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, time
from app.models.assignment import Assignment
from app.models.attachment import Attachment
from app.models.user import User
from app.schemas.assignment import AssignmentOut
from app.router.deps import get_current_active_user
from app.db import get_db

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

# ----------- Get Assignment with id --------------------
@router.get("/assignments/{assignment_id}", response_model=AssignmentOut)
async def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: User = Depends(get_current_active_user),
):
    assignment = (
        db.query(Assignment)
        .filter(Assignment.id == assignment_id)
        .first()
    )
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if (
        assignment.assigned_teacher_id != current_user.id
        and current_user.id not in [s.id for s in assignment.students]
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    return AssignmentOut.model_validate(
        assignment, from_attributes=True, context={"request": request}
    )


# ----------------------- Get Assignment --------------------------====
@router.get("/assignments", response_model=List[AssignmentOut])
async def list_assignments(
    db: Session = Depends(get_db),
    request: Request = None,
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == "teacher":
        assignments = db.query(Assignment).filter(
            Assignment.assigned_teacher_id == current_user.id
        ).all()
    else:
        assignments = (
            db.query(Assignment)
            .join(Assignment.students)
            .filter(User.id == current_user.id)
            .all()
        )

    return [
        AssignmentOut.model_validate(a, from_attributes=True, context={"request": request})
        for a in assignments
    ]