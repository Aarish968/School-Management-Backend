from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from core.config import settings
# from app.db import engine
# from app.db import Base
from fastapi.staticfiles import StaticFiles
from db import engine
from base import Base
from router.v1 import auth, users, attendance, assignment

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="School Management System API",
    description="A comprehensive API for managing school operations including students, teachers, courses, and grades.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static folder for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",   # example React port
        "http://yourdomain.com"    # production domain
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # CORS_ALLOW_ALL_ORIGINS = True,
    # CORS_ALLOW_CREDENTIALS = True
)


# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(attendance.router, prefix="/api/v1", tags=["Attendance"])
app.include_router(assignment.router, prefix="/api/v1", tags=["Assignment"])
# app.include_router(courses.router, prefix="/api/v1/courses", tags=["courses"])
# app.include_router(grades.router, prefix="/api/v1/grades", tags=["grades"])


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to School Management System API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
