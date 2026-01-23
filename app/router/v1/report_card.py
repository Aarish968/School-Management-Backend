# router/v1/report_card.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db import get_db
from app.models.user import User as UserModel
from app.schemas.report_card import (
    ReportCardCreate, 
    ReportCardUpdate, 
    ReportCardResponse, 
    StudentReportCardSummary,
    ClassReportSummary
)
from app.crud.report_card import (
    create_report_card,
    get_report_card,
    get_report_cards,
    update_report_card,
    delete_report_card,
    get_student_report_card_summary,
    get_class_report_summary,
    publish_report_cards
)
from app.router.deps import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ReportCardResponse)
async def create_report_card_endpoint(
    report_card_data: ReportCardCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Create a new report card (Teacher only)"""
    try:
        # Check if user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can create report cards"
            )
        
        # Set teacher_id to current user
        report_card_data.teacher_id = current_user.id
        
        report_card = create_report_card(db, report_card_data)
        
        # Add related data for response
        report_card.student_name = report_card.student.full_name if report_card.student else None
        report_card.teacher_name = report_card.teacher.full_name if report_card.teacher else None
        report_card.subject_name = report_card.subject.name if report_card.subject else None
        report_card.subject_code = report_card.subject.code if report_card.subject else None
        
        return report_card
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating report card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create report card"
        )


@router.get("/", response_model=List[ReportCardResponse])
async def get_report_cards_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    student_id: Optional[int] = Query(None),
    subject_id: Optional[int] = Query(None),
    academic_year: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    term: Optional[str] = Query(None),
    is_published: Optional[bool] = Query(None),
    is_final: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get report cards with filters"""
    try:
        # Filter based on user role
        teacher_id = None
        if current_user.role == "teacher":
            teacher_id = current_user.id
        elif current_user.role == "student":
            student_id = current_user.id
            is_published = True  # Students can only see published report cards
        
        report_cards = get_report_cards(
            db=db,
            skip=skip,
            limit=limit,
            student_id=student_id,
            teacher_id=teacher_id,
            subject_id=subject_id,
            academic_year=academic_year,
            semester=semester,
            term=term,
            is_published=is_published,
            is_final=is_final
        )
        
        # Add related data for response
        for report_card in report_cards:
            report_card.student_name = report_card.student.full_name if report_card.student else None
            report_card.teacher_name = report_card.teacher.full_name if report_card.teacher else None
            report_card.subject_name = report_card.subject.name if report_card.subject else None
            report_card.subject_code = report_card.subject.code if report_card.subject else None
        
        return report_cards
        
    except Exception as e:
        logger.error(f"Error fetching report cards: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch report cards"
        )


@router.get("/student/{student_id}/summary", response_model=StudentReportCardSummary)
async def get_student_report_card_summary_endpoint(
    student_id: int,
    academic_year: str = Query(...),
    semester: Optional[str] = Query(None),
    term: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get student's complete report card summary"""
    try:
        # Check permissions
        if current_user.role == "student" and current_user.id != student_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students can only view their own report cards"
            )
        
        summary = get_student_report_card_summary(
            db=db,
            student_id=student_id,
            academic_year=academic_year,
            semester=semester,
            term=term
        )
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No report cards found for the specified period"
            )
        
        # Add related data for report cards
        for report_card in summary["report_cards"]:
            report_card.student_name = report_card.student.full_name if report_card.student else None
            report_card.teacher_name = report_card.teacher.full_name if report_card.teacher else None
            report_card.subject_name = report_card.subject.name if report_card.subject else None
            report_card.subject_code = report_card.subject.code if report_card.subject else None
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching student report card summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch report card summary"
        )


@router.get("/class/summary", response_model=ClassReportSummary)
async def get_class_report_summary_endpoint(
    academic_year: str = Query(...),
    class_level: Optional[int] = Query(None),
    department: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    term: Optional[str] = Query(None),
    institution_type: str = Query("school"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get class-wise report summary (Teacher/Admin only)"""
    try:
        # Check permissions
        if current_user.role not in ["teacher", "admin"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers and admins can view class summaries"
            )
        
        summary = get_class_report_summary(
            db=db,
            class_level=class_level,
            department=department,
            academic_year=academic_year,
            semester=semester,
            term=term,
            institution_type=institution_type
        )
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No report cards found for the specified class/period"
            )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching class report summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch class report summary"
        )


@router.get("/{report_card_id}", response_model=ReportCardResponse)
async def get_report_card_endpoint(
    report_card_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Get report card by ID"""
    try:
        report_card = get_report_card(db, report_card_id)
        if not report_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report card not found"
            )
        
        # Check permissions
        if current_user.role == "student":
            if current_user.id != report_card.student_id or not report_card.is_published:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
        elif current_user.role == "teacher":
            if current_user.id != report_card.teacher_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Teachers can only view their own report cards"
                )
        
        # Add related data for response
        report_card.student_name = report_card.student.full_name if report_card.student else None
        report_card.teacher_name = report_card.teacher.full_name if report_card.teacher else None
        report_card.subject_name = report_card.subject.name if report_card.subject else None
        report_card.subject_code = report_card.subject.code if report_card.subject else None
        
        return report_card
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching report card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch report card"
        )


@router.put("/{report_card_id}", response_model=ReportCardResponse)
async def update_report_card_endpoint(
    report_card_id: int,
    report_card_data: ReportCardUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Update report card (Teacher only)"""
    try:
        # Check if user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can update report cards"
            )
        
        # Check if report card exists and belongs to teacher
        existing_report_card = get_report_card(db, report_card_id)
        if not existing_report_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report card not found"
            )
        
        if existing_report_card.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only update their own report cards"
            )
        
        report_card = update_report_card(db, report_card_id, report_card_data)
        
        # Add related data for response
        report_card.student_name = report_card.student.full_name if report_card.student else None
        report_card.teacher_name = report_card.teacher.full_name if report_card.teacher else None
        report_card.subject_name = report_card.subject.name if report_card.subject else None
        report_card.subject_code = report_card.subject.code if report_card.subject else None
        
        return report_card
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating report card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update report card"
        )


@router.delete("/{report_card_id}")
async def delete_report_card_endpoint(
    report_card_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Delete report card (Teacher only)"""
    try:
        # Check if user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can delete report cards"
            )
        
        # Check if report card exists and belongs to teacher
        existing_report_card = get_report_card(db, report_card_id)
        if not existing_report_card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report card not found"
            )
        
        if existing_report_card.teacher_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Teachers can only delete their own report cards"
            )
        
        success = delete_report_card(db, report_card_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report card not found"
            )
        
        return {"message": "Report card deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting report card: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete report card"
        )


@router.post("/publish")
async def publish_report_cards_endpoint(
    report_card_ids: List[int],
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """Publish multiple report cards (Teacher only)"""
    try:
        # Check if user is a teacher
        if current_user.role != "teacher":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only teachers can publish report cards"
            )
        
        # Verify all report cards belong to the teacher
        for report_card_id in report_card_ids:
            report_card = get_report_card(db, report_card_id)
            if not report_card or report_card.teacher_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Report card {report_card_id} not found or access denied"
                )
        
        published_report_cards = publish_report_cards(db, report_card_ids)
        
        return {
            "message": f"Successfully published {len(published_report_cards)} report cards",
            "published_count": len(published_report_cards)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error publishing report cards: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish report cards"
        )