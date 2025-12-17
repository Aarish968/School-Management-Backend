from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# Base for creating users (required fields)
class UserBase(BaseModel):
    email: str
    full_name: Optional[str]
    role: str
    institution_type: Optional[str] = None   # ✅ include this

    
    class Config:
        from_attributes=True
        orm_mode = True


class UserCreate(UserBase):
    password: str
    username: Optional[str] = None


class UserOut(BaseModel):
    id: int
    # name: str  # or whatever fields you want to expose

    class Config:
        orm_mode = True


# ---------------------- Updates Schemas ----------------------
# Schema for updates (all fields optional)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    subject: Optional[str] = None
    classes: Optional[int] = None
    department: Optional[str] = None
    institution_type: Optional[str] = None
    image: Optional[str] = None
    address: Optional[str] = None
    teacher_dept_id: Optional[int] = None
    age: Optional[int] = None



# ---------------------- Auth Me Schemas ----------------------
class UserInDB(BaseModel):
    id: int
    email: EmailStr
    username: str
    full_name: Optional[str]
    role: str
    image: Optional[str]
    address: Optional[str]
    teacher_dept_id: Optional[int]
    subject: Optional[str] 
    classes: Optional[int] 
    department: Optional[str] 
    institution_type: Optional[str] 
    age: Optional[int]
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserInDB):
    pass



# ---------------------- Login Schemas ----------------------
class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserTokenResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    institution_type: Optional[str]
    
    class Config:
        from_attributes = True
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserTokenResponse


class TokenData(BaseModel):
    email: Optional[str] = None


# ---------------------- Student Schemas ----------------------

# School student schema
class StudentSchool(BaseModel):
    id: int
    full_name: str
    classes: Optional[int]
    email: str
    institution_type: str 


class Config:
    orm_mode = True




# College student schema
class StudentCollege(BaseModel):
    id: int
    full_name: str
    department: Optional[str]
    email: str
    institution_type: str 


    class Config:
        orm_mode = True




# Wrapper schema for grouped response
class StudentResponse(BaseModel):
    school_students: List[StudentSchool]
    college_students: List[StudentCollege]


# ---------------------- Teacher Schemas ----------------------
class TeacherSchool(BaseModel):
    id: int
    full_name: str
    subject: Optional[str]
    email: str
    institution_type: str


    class Config:
        orm_mode = True




class TeacherCollege(BaseModel):
    id: int
    full_name: str
    department: Optional[str]
    email: str
    institution_type: str


    class Config:
        orm_mode = True




class TeacherResponse(BaseModel):
    school_teachers: List[TeacherSchool]
    college_teachers: List[TeacherCollege]