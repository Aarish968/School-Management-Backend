# models/__init__.py
from .user import User
from .payment import Payment
from .attendance import Attendance
from .assignment import Assignment
from .attachment import Attachment

__all__ = ["User", "Payment", "Attendance", "Assignment", "Attachment"]