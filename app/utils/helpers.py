import uuid
import re
from datetime import datetime
from typing import Optional


def generate_unique_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def generate_student_id(grade_level: str, year: int = None) -> str:
    """Generate a student ID based on grade level and year."""
    if year is None:
        year = datetime.now().year
    
    # Generate a random 4-digit number
    random_num = str(uuid.uuid4().int)[:4]
    return f"{year}{grade_level}{random_num}"


def generate_teacher_id(department: str, year: int = None) -> str:
    """Generate a teacher ID based on department and year."""
    if year is None:
        year = datetime.now().year
    
    # Generate a random 3-digit number
    random_num = str(uuid.uuid4().int)[:3]
    dept_code = department[:3].upper()
    return f"{year}{dept_code}{random_num}"


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15


def format_phone(phone: str) -> str:
    """Format phone number to standard format."""
    digits_only = re.sub(r'\D', '', phone)
    if len(digits_only) == 10:
        return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
    elif len(digits_only) == 11 and digits_only[0] == '1':
        return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
    else:
        return phone


def calculate_grade_percentage(score: float, max_score: float) -> float:
    """Calculate grade percentage."""
    if max_score == 0:
        return 0.0
    return (score / max_score) * 100


def get_letter_grade(percentage: float) -> str:
    """Convert percentage to letter grade."""
    if percentage >= 93:
        return "A"
    elif percentage >= 90:
        return "A-"
    elif percentage >= 87:
        return "B+"
    elif percentage >= 83:
        return "B"
    elif percentage >= 80:
        return "B-"
    elif percentage >= 77:
        return "C+"
    elif percentage >= 73:
        return "C"
    elif percentage >= 70:
        return "C-"
    elif percentage >= 67:
        return "D+"
    elif percentage >= 63:
        return "D"
    elif percentage >= 60:
        return "D-"
    else:
        return "F"


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d") -> Optional[datetime]:
    """Parse string to datetime."""
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing special characters."""
    # Remove or replace special characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized
