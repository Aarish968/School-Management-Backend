# models/payment.py
from sqlalchemy import Boolean, Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.base import Base
# from app.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)  # Amount in INR
    currency = Column(String, default="INR")
    status = Column(String, default="pending")  # pending, paid, failed, refunded
    gateway = Column(String, default="razorpay")  # razorpay, stripe, etc.
    transaction_id = Column(String, nullable=True)  # Gateway transaction ID
    razorpay_order_id = Column(String, nullable=True)  # Razorpay order ID
    razorpay_payment_id = Column(String, nullable=True)  # Razorpay payment ID
    razorpay_signature = Column(String, nullable=True)  # Razorpay signature for verification
    payment_type = Column(String, default="registration")  # registration, fees, etc.
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    paid_at = Column(DateTime(timezone=True), nullable=True)

    # Relations
    student = relationship("User", back_populates="payments")