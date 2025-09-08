# School Management System API

A comprehensive FastAPI-based backend for managing school operations including students, teachers, courses, grades, and attendance.

## Features

- **User Management**: Authentication, authorization, and user roles (admin, teacher, student, parent)
- **Student Management**: Student profiles, enrollment, and grade tracking
- **Course Management**: Course creation, assignment to teachers, and enrollment
- **Grade Management**: Assignment grades, grade calculation, and reporting
- **Attendance Tracking**: Student attendance recording and monitoring
- **Database Migrations**: Alembic for schema evolution
- **API Documentation**: Auto-generated Swagger/OpenAPI documentation

## Project Structure

```
backend/
├── core/
│   ├── config.py          # Environment variables and settings
│   └── security.py        # Password hashing and JWT tokens
├── db/
│   ├── database.py        # SQLAlchemy engine and session
│   └── models.py          # Database models (User, Student, Course, etc.)
├── schemas/
│   ├── user.py           # Pydantic schemas for user operations
│   ├── student.py        # Pydantic schemas for student operations
│   ├── course.py         # Pydantic schemas for course operations
│   └── grade.py          # Pydantic schemas for grade operations
├── crud/
│   ├── user.py           # User CRUD operations
│   ├── student.py        # Student CRUD operations
│   └── course.py         # Course CRUD operations
├── router/
│   ├── deps.py           # FastAPI dependencies
│   └── v1/
│       ├── auth.py       # Authentication endpoints
│       ├── users.py      # User management endpoints
│       ├── students.py   # Student management endpoints
│       └── courses.py    # Course management endpoints
├── utils/
│   └── helpers.py        # Utility functions
├── alembic/              # Database migration scripts
├── main.py              # FastAPI application entry point
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory (use `env_example.txt` as a template):
   ```env
   # Database Configuration
   DATABASE_HOST=localhost
   DATABASE_PORT=5432
   DATABASE_NAME=school_management
   DATABASE_USER=your_username
   DATABASE_PASSWORD=your_password
   
   # Security Configuration
   SECRET_KEY=your-secret-key-change-in-production
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Set up PostgreSQL database**
   ```bash
   # Create database and test connection
   python setup_database.py
   
   # Run database migrations
   alembic upgrade head
   ```

6. **Start the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user

### Users
- `GET /api/v1/users/` - List all users (admin only)
- `POST /api/v1/users/` - Create new user (admin only)
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user (admin only)
- `DELETE /api/v1/users/{user_id}` - Delete user (admin only)
- `GET /api/v1/users/role/{role}` - Get users by role

### Students
- `GET /api/v1/students/` - List all students
- `POST /api/v1/students/` - Create new student (admin only)
- `GET /api/v1/students/{student_id}` - Get student by ID
- `GET /api/v1/students/{student_id}/with-user` - Get student with user info
- `PUT /api/v1/students/{student_id}` - Update student (admin only)
- `DELETE /api/v1/students/{student_id}` - Delete student (admin only)
- `GET /api/v1/students/grade/{grade_level}` - Get students by grade

### Courses
- `GET /api/v1/courses/` - List all courses
- `GET /api/v1/courses/active` - List active courses only
- `POST /api/v1/courses/` - Create new course (admin only)
- `GET /api/v1/courses/{course_id}` - Get course by ID
- `GET /api/v1/courses/{course_id}/with-teacher` - Get course with teacher info
- `PUT /api/v1/courses/{course_id}` - Update course (admin only)
- `DELETE /api/v1/courses/{course_id}` - Delete course (admin only)
- `GET /api/v1/courses/teacher/{teacher_id}` - Get courses by teacher

## Database Models

### User
- Basic user information (email, username, password)
- Role-based access control
- Active/inactive status

### Student
- Student-specific information (grade level, date of birth, etc.)
- Linked to User model
- Enrollment and grade tracking

### Teacher
- Teacher-specific information (department, qualifications)
- Linked to User model
- Course assignments

### Course
- Course information (code, name, description, credits)
- Teacher assignment
- Student enrollment capacity

### Enrollment
- Student-course relationships
- Enrollment status tracking

### Grade
- Assignment grades and scores
- Grade types (assignment, quiz, exam, final)
- Percentage and letter grade calculation

### Attendance
- Student attendance tracking
- Status types (present, absent, late, excused)

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for password security
- **Role-based Access Control**: Different permissions for different user roles
- **CORS Support**: Configurable cross-origin resource sharing

## Development

### Running Tests
```bash
# Add test dependencies and run tests
pip install pytest pytest-asyncio httpx
pytest
```

### Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Formatting
```bash
# Install formatting tools
pip install black isort

# Format code
black .
isort .
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_HOST` | Database host | `localhost` |
| `DATABASE_PORT` | Database port | `5432` |
| `DATABASE_NAME` | Database name | `school_management` |
| `DATABASE_USER` | Database username | `postgres` |
| `DATABASE_PASSWORD` | Database password | `` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | `30` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000"]` |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.
