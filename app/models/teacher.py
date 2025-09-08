from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from base import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    teacher_id = Column(String, unique=True, index=True)
    department = Column(String)
    hire_date = Column(DateTime(timezone=True), server_default=func.now())
    qualification = Column(String)
    phone = Column(String)
    
    # Relationships
    user = relationship("User", backref="teacher_profile")
    courses = relationship("Course", back_populates="teacher")
