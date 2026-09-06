from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.api.deps import get_current_user, require_admin, get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.user_service import user_service

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve details of the currently authenticated user."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_me(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update profile information for the currently authenticated user."""
    updated_user = user_service.update(db, user=current_user, user_in=user_in)
    return updated_user


# Backward compatibility alias for /profile
@router.put("/profile", response_model=UserResponse)
def update_user_profile_alias(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Alias for /users/me profile update."""
    return update_current_user_me(user_in, db, current_user)


@router.get("/", response_model=List[UserResponse], dependencies=[Depends(require_admin)])
def list_users(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> Any:
    """List registered users (Administrator only)."""
    stmt = select(User).offset(skip).limit(limit)
    users = db.execute(stmt).scalars().all()
    return users
