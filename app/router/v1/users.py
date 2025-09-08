from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db import get_db
from crud.user import (
    get_user, get_users, create_user, update_user, delete_user, get_users_by_role
)
from schemas.user import User, UserCreate, UserUpdate
from router.deps import get_current_active_user, get_current_superuser

router = APIRouter()


@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=User)
def create_user_endpoint(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Create new user.
    """
    user = create_user(db, user=user_in)
    return user


@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: int,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    return user


@router.put("/{user_id}", response_model=User)
def update_user_endpoint(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Update a user.
    """
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    user = update_user(db, user_id=user_id, user_update=user_in)
    return user


@router.delete("/{user_id}")
def delete_user_endpoint(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user = Depends(get_current_superuser),
) -> Any:
    """
    Delete a user.
    """
    user = get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    delete_user(db, user_id=user_id)
    return {"message": "User deleted successfully"}


@router.get("/role/{role}", response_model=List[User])
def read_users_by_role(
    role: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_active_user),
) -> Any:
    """
    Retrieve users by role.
    """
    users = get_users_by_role(db, role=role, skip=skip, limit=limit)
    return users
