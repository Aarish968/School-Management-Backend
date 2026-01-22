# services/razorpay_service.py
import razorpay
import hmac
import hashlib
from app.core.config import settings
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class RazorpayService:
    def __init__(self):
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    def create_order(self, amount: float, currency: str = "INR", receipt: str = None) -> Dict[str, Any]:
        """
        Create a Razorpay order
        Amount should be in INR, will be converted to paise
        """
        try:
            # Convert amount to paise (multiply by 100)
            amount_in_paise = int(amount * 100)
            
            order_data = {
                "amount": amount_in_paise,
                "currency": currency,
                "receipt": receipt or f"receipt_{amount_in_paise}",
                "payment_capture": 1  # Auto capture payment
            }
            
            logger.info(f"Before of client-----------------------")
            order = self.client.order.create(data=order_data)
            logger.info(f"After of client-----------------------")
            logger.info(f"Razorpay order created: {order['id']}")
            return order
            
        except Exception as e:
            logger.error(f"Error creating Razorpay order: {str(e)}")
            raise Exception(f"Failed to create payment order: {str(e)}")
    
    def verify_payment_signature(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str) -> bool:
        """
        Verify Razorpay payment signature
        """
        try:
            # Create the signature string
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            
            # Generate signature using HMAC SHA256
            generated_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode(),
                message.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            is_valid = hmac.compare_digest(generated_signature, razorpay_signature)
            
            if is_valid:
                logger.info(f"Payment signature verified for order: {razorpay_order_id}")
            else:
                logger.warning(f"Invalid payment signature for order: {razorpay_order_id}")
                
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying payment signature: {str(e)}")
            return False
    
    def get_payment_details(self, payment_id: str) -> Dict[str, Any]:
        """
        Get payment details from Razorpay
        """
        try:
            payment = self.client.payment.fetch(payment_id)
            return payment
        except Exception as e:
            logger.error(f"Error fetching payment details: {str(e)}")
            raise Exception(f"Failed to fetch payment details: {str(e)}")


# Create a singleton instance
razorpay_service = RazorpayService()