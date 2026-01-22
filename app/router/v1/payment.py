# router/v1/payment.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db import get_db
from app.models.user import User as UserModel
from app.schemas.payment import (
    PaymentCreate, 
    PaymentResponse, 
    RazorpayOrderCreate, 
    RazorpayOrderResponse,
    PaymentVerification,
    PaymentUpdate
)
from app.crud.payment import (
    create_payment, 
    get_payment_by_id, 
    get_payment_by_order_id,
    get_payments_by_student,
    update_payment_by_order_id,
    update_payment
)
from app.services.razorpay_service import razorpay_service
from app.router.deps import get_current_active_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/create-order", response_model=RazorpayOrderResponse)
async def create_payment_order(
    order_data: RazorpayOrderCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Create a Razorpay order for student registration payment
    """
    try:
        # Only students can create payment orders for registration
        if current_user.role != "student":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only students can create registration payment orders"
            )
        
        # Create Razorpay order
        receipt = f"reg_{current_user.id}_{current_user.email}"
        razorpay_order = razorpay_service.create_order(
            amount=order_data.amount,
            currency=order_data.currency,
            receipt=receipt
        )
        
        # Create payment record in database
        payment_data = PaymentCreate(
            student_id=current_user.id,
            amount=order_data.amount,
            currency=order_data.currency,
            payment_type="registration",
            description=f"Registration fee for {current_user.full_name}"
        )
        
        db_payment = create_payment(db, payment_data)
        
        # Update payment with Razorpay order ID
        payment_update = PaymentUpdate(
            razorpay_order_id=razorpay_order["id"],
            status="pending"
        )
        update_payment_by_order_id(db, razorpay_order["id"], payment_update)
        
        return RazorpayOrderResponse(
            id=razorpay_order["id"],
            amount=razorpay_order["amount"],
            currency=razorpay_order["currency"],
            receipt=razorpay_order.get("receipt"),
            status=razorpay_order["status"]
        )
        
    except Exception as e:
        logger.error(f"Error creating payment order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment order: {str(e)}"
        )


# New endpoint for guest payment order creation (during signup)
@router.post("/create-guest-order", response_model=RazorpayOrderResponse)
async def create_guest_payment_order(
    order_data: dict,  # Accept dict to handle additional fields
    db: Session = Depends(get_db)
):
    """
    Create a Razorpay order for guest user (during signup process)
    """
    try:
        amount = order_data.get("amount", 50.0)
        currency = order_data.get("currency", "INR")
        email = order_data.get("email", "")
        full_name = order_data.get("full_name", "")
        
        # Create Razorpay order
        receipt = f"guest_reg_{email}"
        razorpay_order = razorpay_service.create_order(
            amount=amount,
            currency=currency,
            receipt=receipt
        )
        
        # Store order details temporarily (we'll create payment record after user signup)
        # For now, just return the order details
        return RazorpayOrderResponse(
            id=razorpay_order["id"],
            amount=razorpay_order["amount"],
            currency=razorpay_order["currency"],
            receipt=razorpay_order.get("receipt"),
            status=razorpay_order["status"]
        )
        
    except Exception as e:
        logger.error(f"Error creating guest payment order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment order: {str(e)}"
        )


@router.post("/verify-payment")
async def verify_payment(
    verification_data: PaymentVerification,
    db: Session = Depends(get_db)
):
    """
    Verify Razorpay payment and update payment status
    """
    try:
        # Verify payment signature
        is_valid = razorpay_service.verify_payment_signature(
            verification_data.razorpay_order_id,
            verification_data.razorpay_payment_id,
            verification_data.razorpay_signature
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment signature"
            )
        
        # Check if payment record exists
        existing_payment = get_payment_by_order_id(db, verification_data.razorpay_order_id)
        
        if existing_payment:
            # Update existing payment
            payment_update = PaymentUpdate(
                status="paid",
                razorpay_payment_id=verification_data.razorpay_payment_id,
                razorpay_signature=verification_data.razorpay_signature,
                transaction_id=verification_data.razorpay_payment_id
            )
            
            updated_payment = update_payment_by_order_id(
                db, 
                verification_data.razorpay_order_id, 
                payment_update
            )
        else:
            # Create new payment record (for guest payments)
            payment_data = PaymentCreate(
                student_id=verification_data.student_id,
                amount=50.0,  # Registration fee
                currency="INR",
                payment_type="registration",
                description="Registration fee payment"
            )
            
            new_payment = create_payment(db, payment_data)
            
            # Update with payment details
            payment_update = PaymentUpdate(
                razorpay_order_id=verification_data.razorpay_order_id,
                status="paid",
                razorpay_payment_id=verification_data.razorpay_payment_id,
                razorpay_signature=verification_data.razorpay_signature,
                transaction_id=verification_data.razorpay_payment_id
            )
            
            updated_payment = update_payment(db, new_payment.id, payment_update)
        
        if not updated_payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment record not found"
            )
        
        # Get payment details from Razorpay for additional verification
        try:
            payment_details = razorpay_service.get_payment_details(verification_data.razorpay_payment_id)
            logger.info(f"Payment verified successfully: {verification_data.razorpay_payment_id}")
        except Exception as e:
            logger.warning(f"Could not fetch payment details from Razorpay: {str(e)}")
        
        return {
            "success": True,
            "message": "Payment verified successfully",
            "payment_id": updated_payment.id,
            "status": updated_payment.status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify payment: {str(e)}"
        )


@router.get("/my-payments", response_model=List[PaymentResponse])
async def get_my_payments(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get all payments for the current user
    """
    try:
        payments = get_payments_by_student(db, current_user.id)
        return payments
    except Exception as e:
        logger.error(f"Error fetching user payments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payments"
        )


@router.get("/payment/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    Get specific payment details
    """
    try:
        payment = get_payment_by_id(db, payment_id)
        
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        
        # Check if user owns this payment or is admin
        if payment.student_id != current_user.id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this payment"
            )
        
        return payment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch payment"
        )