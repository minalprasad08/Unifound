from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserWithToken
from app.services.user_service import user_service
from app.core.rate_limiter import rate_limit_login, rate_limit_register

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_register)],
)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
) -> Any:
    """Register a new user account. Public registration creates standard USER accounts only."""
    existing_user = user_service.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )
    user = user_service.create_public_user(db, user_in=user_in)
    return user


@router.post(
    "/login",
    response_model=UserWithToken,
    dependencies=[Depends(rate_limit_login)],
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
) -> Any:
    """Log in with email and password returning JWT access token and profile."""
    user = user_service.authenticate(
        db, email=login_data.email, password=login_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
        expires_delta=access_token_expires,
    )

    return {
        "user": user,
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/token", response_model=Token)
def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Any:
    """OAuth2 compatible token login for Swagger UI and CLI tools."""
    user = user_service.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user account.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        subject=user.id,
        role=user.role.value,
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve details of the currently authenticated user."""
    return current_user
