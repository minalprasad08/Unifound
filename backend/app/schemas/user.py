from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=30)
    department: Optional[str] = Field(None, max_length=100)
    student_id: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    # Role defaults to USER. Public registration ignores any attempt to specify ADMIN.
    role: Optional[UserRole] = UserRole.USER


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=30)
    department: Optional[str] = Field(None, max_length=100)
    student_id: Optional[str] = Field(None, max_length=50)
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserWithToken(BaseModel):
    user: UserResponse
    access_token: str
    token_type: str = "bearer"
