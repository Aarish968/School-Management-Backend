from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_HOST: str 
    DATABASE_PORT: int
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str

    # Razorpay Settings
    RAZORPAY_KEY_ID: str = "rzp_test_S6saCTUVL3j21k"
    RAZORPAY_KEY_SECRET: str = "v9VVs4eO5664j2HEWuQFlYe7" 
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL from components."""
        if self.DATABASE_PASSWORD:
            return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        else:
            return f"postgresql://{self.DATABASE_USER}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
