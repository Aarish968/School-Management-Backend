# router/v1/subject.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import get_db
from app.models.user import User as UserModel
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.crud.subject import (
    create_subject,
    get_subject,
    get_subjects,
    update_subject,
    delete_subject,
    get_subject_by_code
)
from app.router.deps import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=SubjectResponse)
async def create_subject_endpoint(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new subject (Admin/Teacher only)"""
    try:
        # Check if user has permission (admin or teacher)
        if current_user.role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins and teachers can create subjects"
            )
        
        # Check if subject code already exists
        existing_subject = get_subject_by_code(db, subject_data.code)
        if existing_subject:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Subject with this code already exists"
            )
        
        subject = create_subject(db, subject_data)
        return subject
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subject: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subject"
        )


@router.get("/", response_model=List[SubjectResponse])
async def get_subjects_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    institution_type: Optional[str] = Query(None),
    class_level: Optional[int] = Query(None),
    department: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get subjects with filters"""
    try:
        subjects = get_subjects(
            db=db,
            skip=skip,
            limit=limit,
            institution_type=institution_type,
            class_level=class_level,
            department=department
        )
        return subjects
        
    except Exception as e:
        logger.error(f"Error fetching subjects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subjects"
        )


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get subject by ID"""
    try:
        subject = get_subject(db, subject_id)
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        return subject
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching subject: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subject"
        )


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject_endpoint(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update subject (Admin/Teacher only)"""
    try:
        # Check if user has permission
        if current_user.role not in ["admin", "teacher"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins and teachers can update subjects"
            )
        
        subject = update_subject(db, subject_id, subject_data)
        if not subject:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        return subject
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subject: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subject"
        )


@router.delete("/{subject_id}")
async def delete_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete subject (Admin only)"""
    try:
        # Check if user has permission
        if current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can delete subjects"
            )
        
        success = delete_subject(db, subject_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subject not found"
            )
        
        return {"message": "Subject deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting subject: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete subject"
        )