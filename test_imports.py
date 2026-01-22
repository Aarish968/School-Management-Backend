#!/usr/bin/env python3
"""
Test script to verify all imports are working correctly
Run this from the backend directory: python test_imports.py
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_imports():
    """Test all critical imports"""
    try:
        print("Testing imports...")
        
        # Test core imports
        from app.core.config import settings
        from app.core.security import get_password_hash
        print("✓ Core imports successful")
        
        # Test database imports
        from app.db import get_db, engine
        from app.base import Base
        print("✓ Database imports successful")
        
        # Test model imports
        from app.models.user import User
        from app.models.payment import Payment
        from app.models.attendance import Attendance
        from app.models.assignment import Assignment
        from app.models.attachment import Attachment
        print("✓ Model imports successful")
        
        # Test schema imports
        from app.schemas.user import UserCreate, UserUpdate
        from app.schemas.payment import PaymentCreate, PaymentResponse
        print("✓ Schema imports successful")
        
        # Test CRUD imports
        from app.crud.user import get_user, create_user
        from app.crud.payment import create_payment
        print("✓ CRUD imports successful")
        
        # Test router imports
        from app.router.deps import get_current_active_user
        from app.router.v1.auth import router as auth_router
        from app.router.v1.payment import router as payment_router
        print("✓ Router imports successful")
        
        # Test service imports
        from app.services.razorpay_service import razorpay_service
        print("✓ Service imports successful")
        
        print("\n🎉 All imports successful! Your backend is ready to run.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)