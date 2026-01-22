#!/usr/bin/env python3
"""
Test script to verify configuration loads correctly
"""

import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

try:
    from app.core.config import settings
    print("✓ Configuration loaded successfully")
    print(f"Database Host: {settings.DATABASE_HOST}")
    print(f"Razorpay Key ID: {settings.RAZORPAY_KEY_ID[:10]}...")  # Only show first 10 chars for security
    print(f"Secret Key: {settings.SECRET_KEY[:10]}...")
    print("✓ All configuration values loaded")
except Exception as e:
    print(f"❌ Configuration error: {e}")
    sys.exit(1)