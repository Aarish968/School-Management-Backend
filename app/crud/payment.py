# crud/payment.py
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate
from typing import Optional
from datetime import datetime


def create_payment(db: Session, payment: PaymentCreate) -> Payment:
    """Create a new payment record"""
    db_payment = Payment(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


def get_payment_by_id(db: Session, payment_id: int) -> Optional[Payment]:
    """Get payment by ID"""
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_payment_by_order_id(db: Session, razorpay_order_id: str) -> Optional[Payment]:
    """Get payment by Razorpay order ID"""
    return db.query(Payment).filter(Payment.razorpay_order_id == razorpay_order_id).first()


def get_payments_by_student(db: Session, student_id: int):
    """Get all payments for a student"""
    return db.query(Payment).filter(Payment.student_id == student_id).all()


def update_payment(db: Session, payment_id: int, payment_update: PaymentUpdate) -> Optional[Payment]:
    """Update payment record"""
    db_payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if db_payment:
        update_data = payment_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_payment, field, value)
        
        # Set paid_at timestamp when status changes to paid
        if payment_update.status == "paid" and not db_payment.paid_at:
            db_payment.paid_at = datetime.utcnow()
            
        db.commit()
        db.refresh(db_payment)
    return db_payment


def update_payment_by_order_id(db: Session, razorpay_order_id: str, payment_update: PaymentUpdate) -> Optional[Payment]:
    """Update payment by Razorpay order ID"""
    db_payment = db.query(Payment).filter(Payment.razorpay_order_id == razorpay_order_id).first()
    if db_payment:
        update_data = payment_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_payment, field, value)
        
        # Set paid_at timestamp when status changes to paid
        if payment_update.status == "paid" and not db_payment.paid_at:
            db_payment.paid_at = datetime.utcnow()
            
        db.commit()
        db.refresh(db_payment)
    return db_payment