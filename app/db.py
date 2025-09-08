from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings
# import app.models 
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base 
from core.config import settings
# import models 
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# SQLAlchemy engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        print("Database session error:", e)
        db.rollback()
        raise
    finally:
        db.close()
