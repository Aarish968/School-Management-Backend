# router/v1/grade.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import get_db
from app.models.user import User as UserModel
from app.schemas.grade import GradeCreate, GradeUpdate, GradeResponse, StudentGradesSummary
from app.crud.grade import (
    create_grade,
    get_grade,
    get_grades,
    update_grade,
    delete_grade,
    get_student_grades_summary,
    publish_grades
)
from app.router.deps import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=GradeResponse)
async def create_grade_endpoint(
    grade_data: GradeCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new grade (Teacher only)"""
    try:
        # Check if user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can create grades"
            )
        
        # Set teacher_id to current user
        grade_data.teacher_id = current_user.id
        
        grade = create_grade(db, grade_data)
        
        # Add related data for response
        grade.student_name = grade.student.full_name if grade.student else None
        grade.teacher_name = grade.teacher.full_name if grade.teacher else None
        grade.subject_name = grade.subject.name if grade.subject else None
        grade.subject_code = grade.subject.code if grade.subject else None
        
        return grade
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating grade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create grade"
        )


@router.get("/", response_model=List[GradeResponse])
async def get_grades_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    academic_year: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    term: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get grades with filters"""
    try:
        # Filter based on user role
        teacher_id = None
        if current_user.role == "teacher":
            teacher_id = current_user.id
        elif current_user.role == "student":
            student_id = current_user.id
            is_published = True  # Students can only see published grades
        
        grades = get_grades(
            db=db,
            skip=skip,
            limit=limit,
            student_id=student_id,
            teacher_id=teacher_id,
            subject_id=subject_id,
            academic_year=academic_year,
            semester=semester,
            term=term,
            is_published=is_published
        )
        
        # Add related data for response
        for grade in grades:
            grade.student_name = grade.student.full_name if grade.student else None
            grade.teacher_name = grade.teacher.full_name if grade.teacher else None
            grade.subject_name = grade.subject.name if grade.subject else None
            grade.subject_code = grade.subject.code if grade.subject else None
        
        return grades
        
    except Exception as e:
        logger.error(f"Error fetching grades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch grades"
        )


@router.get("/student/{student_id}/summary", response_model=StudentGradesSummary)
async def get_student_grades_summary_endpoint(
    student_id: int,
    academic_year: str = Query(...),
    semester: Optional[str] = Query(None),
    term: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get student's grades summary"""
    try:
        # Check permissions
        if current_user.role == "student" and current_user.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only view their own grades"
            )
        
        summary = get_student_grades_summary(
            db=db,
            student_id=student_id,
            academic_year=academic_year,
            semester=semester,
            term=term
        )
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No grades found for the specified period"
            )
        
        # Add related data for grades
        for grade in summary["grades"]:
            grade.student_name = grade.student.full_name if grade.student else None
            grade.teacher_name = grade.teacher.full_name if grade.teacher else None
            grade.subject_name = grade.subject.name if grade.subject else None
            grade.subject_code = grade.subject.code if grade.subject else None
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching student grades summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch grades summary"
        )


@router.get("/{grade_id}", response_model=GradeResponse)
async def get_grade_endpoint(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get grade by ID"""
    try:
        grade = get_grade(db, grade_id)
        if not grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grade not found"
            )
        
        # Check permissions
        if current_user.role == "student":
            if current_user.id != grade.student_id or not grade.is_published:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        elif current_user.role == "teacher":
            if current_user.id != grade.teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Teachers can only view their own grades"
                )
        
        # Add related data for response
        grade.student_name = grade.student.full_name if grade.student else None
        grade.teacher_name = grade.teacher.full_name if grade.teacher else None
        grade.subject_name = grade.subject.name if grade.subject else None
        grade.subject_code = grade.subject.code if grade.subject else None
        
        return grade
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching grade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch grade"
        )


@router.put("/{grade_id}", response_model=GradeResponse)
async def update_grade_endpoint(
    grade_id: int,
    grade_data: GradeUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update grade (Teacher only)"""
    try:
        # Check if user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can update grades"
            )
        
        # Check if grade exists and belongs to teacher
        existing_grade = get_grade(db, grade_id)
        if not existing_grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grade not found"
            )
        
        if existing_grade.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only update their own grades"
            )
        
        grade = update_grade(db, grade_id, grade_data)
        
        # Add related data for response
        grade.student_name = grade.student.full_name if grade.student else None
        grade.teacher_name = grade.teacher.full_name if grade.teacher else None
        grade.subject_name = grade.subject.name if grade.subject else None
        grade.subject_code = grade.subject.code if grade.subject else None
        
        return grade
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating grade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update grade"
        )


@router.delete("/{grade_id}")
async def delete_grade_endpoint(
    grade_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete grade (Teacher only)"""
    try:
        # Check if user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can delete grades"
            )
        
        # Check if grade exists and belongs to teacher
        existing_grade = get_grade(db, grade_id)
        if not existing_grade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grade not found"
            )
        
        if existing_grade.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only delete their own grades"
            )
        
        success = delete_grade(db, grade_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Grade not found"
            )
        
        return {"message": "Grade deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting grade: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete grade"
        )


@router.post("/publish")
async def publish_grades_endpoint(
    grade_ids: List[int],
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Publish multiple grades (Teacher only)"""
    try:
        # Check if user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can publish grades"
            )
        
        # Verify all grades belong to the teacher
        for grade_id in grade_ids:
            grade = get_grade(db, grade_id)
            if not grade or grade.teacher_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Grade {grade_id} not found or access denied"
                )
        
        published_grades = publish_grades(db, grade_ids)
        
        return {
            "message": f"Successfully published {len(published_grades)} grades",
            "published_count": len(published_grades)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing grades: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish grades"
        )