import os
import uuid
from datetime import timedelta
from typing import Any, List, Union
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from db import get_db
from models.user import User as UserModel
from core.config import settings
from core.security import create_access_token, verify_token
from crud.user import authenticate_user, create_user, get_user_by_email, update_user
from schemas.user import (User,
UserCreate,
Token, 
UserLogin, 
UserUpdate, 
UserInDB, 
UserUpdate,
StudentSchool, 
StudentCollege, 
StudentResponse, TeacherResponse, TeacherCollege, TeacherSchool)
from router.deps import get_current_active_user

router = APIRouter()


# ---------------------- Login and Access Token Api ----------------------


@router.post("/login", response_model=Token)
def login_access_token(user: UserLogin, db: Session = Depends(get_db)) -> Any:
    user_obj = authenticate_user(db, email=user.email, password=user.password)
    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user_obj.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            data={"sub": user_obj.email}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
        "user": user_obj # Add this line to return user data
    }


# ---------------------- Register Api ----------------------

@router.post("/register", response_model=Token)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    user = create_user(db, user=user_in)
    
    # Create access token for the new user
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }


# ---------------------- Auth Me Api ----------------------

@router.get("/me", response_model=UserInDB)
def read_users_me(
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

# ---------------------- Update Api ----------------------

UPLOAD_DIR = "static/uploads"

@router.put("/me/update", response_model=User)
async def update_profile(
    full_name: str = Form(None),
    username: str = Form(None),
    email: str = Form(None),
    role: str = Form(None),
    address: str = Form(None),
    subject: str = Form(None),
    classes: int = Form(None),
    department: str = Form(None),
    institution_type: str = Form(None),
    teacher_dept_id: int = Form(None),
    age: int = Form(None),
    image: UploadFile = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Update current user's profile with optional fields and image upload.
    """

    update_data = {}

    if full_name:
        update_data["full_name"] = full_name
    if username:
        update_data["username"] = username
    if email:
        update_data["email"] = email
    if role:
        update_data["role"] = role
    if address:
        update_data["address"] = address
    if subject:
        update_data["subject"] = subject
    if classes:
        update_data["classes"] = classes
    if teacher_dept_id is not None:
        update_data["teacher_dept_id"] = teacher_dept_id
    if department:
        update_data["department"] = department
    if institution_type:
        update_data["institution_type"] = institution_type
    if age is not None:
        update_data["age"] = age

    # Handle image upload
    if image:
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        ext = os.path.splitext(image.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())

        update_data["image"] = f"/{UPLOAD_DIR}/{filename}"

    db_user = update_user(db=db, user_id=current_user.id, user_update=UserUpdate(**update_data))

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return db_user

# ---------------------- get Students Api ----------------------

@router.get("/students", response_model=StudentResponse)
def get_students(db: Session = Depends(get_db)):
    try:
        students = db.query(UserModel).filter(UserModel.role == "student").all()

        school_students: List[StudentSchool] = []
        college_students: List[StudentCollege] = []

        for s in students:
            if s.institution_type == "school":
                school_students.append(
                    StudentSchool(
                        id=s.id,
                        full_name=s.full_name,
                        classes=s.classes,
                        email=s.email,
                        institution_type=s.institution_type,
                    )
                )
            elif s.institution_type == "college":
                college_students.append(
                    StudentCollege(
                        id=s.id,
                        full_name=s.full_name,
                        department=s.department,
                        email=s.email,
                        institution_type=s.institution_type,
                    )
                )

        return StudentResponse(school_students=school_students, college_students=college_students)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving students: {str(e)}")

# ---------------------- get Teacher Api ----------------------

@router.get("/teachers", response_model=TeacherResponse)
def get_teachers(db: Session = Depends(get_db)):
    try:
        teachers = db.query(UserModel).filter(UserModel.role == "teacher").all()


        school_teachers: List[TeacherSchool] = []
        college_teachers: List[TeacherCollege] = []


        for t in teachers:
            if t.institution_type == "school":
                school_teachers.append(
                    TeacherSchool(
                    id=t.id,
                    full_name=t.full_name,
                    subject=t.subject,
                    email=t.email,
                    institution_type=t.institution_type,
            )
            )
            elif t.institution_type == "college":
                college_teachers.append(
                    TeacherCollege(
                    id=t.id,
                    full_name=t.full_name,
                    department=t.department,
                    email=t.email,
                    institution_type=t.institution_type,
                )
            )


        return TeacherResponse(school_teachers=school_teachers, college_teachers=college_teachers)


    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving teachers: {str(e)}")