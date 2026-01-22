# schemas/payment.py
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaymentBase(BaseModel):
    amount: float
    currency: str = "INR"
    payment_type: str = "registration"
    description: Optional[str] = None

    class Config:
        from_attributes = True


class PaymentCreate(PaymentBase):
    student_id: int


class PaymentUpdate(BaseModel):
    status: Optional[str] = None
    transaction_id: Optional[str] = None
    razorpay_payment_id: Optional[str] = None
    razorpay_signature: Optional[str] = None
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentResponse(PaymentBase):
    id: int
    student_id: int
    status: str
    gateway: str
    razorpay_order_id: Optional[str]
    razorpay_payment_id: Optional[str]
    transaction_id: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    paid_at: Optional[datetime]

    class Config:
        from_attributes = True


class RazorpayOrderCreate(BaseModel):
    amount: float = 50.0  # Default ₹50 for student registration
    currency: str = "INR"
    receipt: Optional[str] = None


class RazorpayOrderResponse(BaseModel):
    id: str  # Razorpay order ID
    amount: int  # Amount in paise
    currency: str
    receipt: Optional[str]
    status: str


class PaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    student_id: int