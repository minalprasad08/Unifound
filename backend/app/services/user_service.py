import os
import logging
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password

logger = logging.getLogger("unifound.user_service")


class UserService:
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.get(User, user_id)

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        stmt = select(User).where(func.lower(User.email) == email.lower().strip())
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def create(db: Session, user_in: UserCreate, force_role: Optional[UserRole] = None) -> User:
        """Create a new user with secure password hash. Supports explicit role override for internal/admin flows."""
        hashed_password = get_password_hash(user_in.password)
        assigned_role = force_role if force_role is not None else (user_in.role or UserRole.USER)
        
        db_user = User(
            email=user_in.email.lower().strip(),
            password_hash=hashed_password,
            full_name=user_in.full_name.strip(),
            role=assigned_role,
            phone=user_in.phone.strip() if user_in.phone else None,
            department=user_in.department.strip() if user_in.department else None,
            student_id=user_in.student_id.strip() if user_in.student_id else None,
            avatar_url=user_in.avatar_url,
            is_active=True,
            is_verified=False,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def create_public_user(db: Session, user_in: UserCreate) -> User:
        """Public registration: STRICTLY forces role to UserRole.USER. Rejects/ignores any admin request."""
        return UserService.create(db, user_in, force_role=UserRole.USER)

    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        user = UserService.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def update(db: Session, user: User, user_in: UserUpdate) -> User:
        update_data = user_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def deactivate(db: Session, user: User) -> User:
        """Soft-deactivate a user instead of destroying historical items, claims, or audit logs."""
        user.is_active = False
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def count(db: Session) -> int:
        return db.scalar(select(func.count(User.id))) or 0

    @staticmethod
    def ensure_initial_admin(db: Session) -> Optional[User]:
        """
        Secure admin initialization:
        Checks if an admin user exists. If not, creates one from environment variables:
        ADMIN_INITIAL_EMAIL, ADMIN_INITIAL_PASSWORD.
        In production, if credentials are not explicitly supplied, does not create an admin with a static default password.
        """
        existing_admin = db.execute(
            select(User).where(User.role == UserRole.ADMIN)
        ).scalars().first()

        if existing_admin:
            return existing_admin

        admin_email = os.getenv("ADMIN_INITIAL_EMAIL")
        admin_password = os.getenv("ADMIN_INITIAL_PASSWORD")

        # In non-production development environments, provide a convenient dev setup if env is absent
        is_production = os.getenv("ENVIRONMENT", "").lower() == "production"

        if is_production:
            if not admin_email or not admin_password:
                logger.warning("No admin user found and ADMIN_INITIAL_EMAIL/PASSWORD not set in production. Skipping admin auto-seed.")
                return None
        else:
            # Development fallback
            admin_email = admin_email or "admin@campus.edu"
            admin_password = admin_password or "AdminPass123!"

        admin_user = User(
            email=admin_email.lower().strip(),
            password_hash=get_password_hash(admin_password),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            department="Campus Security",
            is_active=True,
            is_verified=True,
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        logger.info(f"Initialized administrator account: {admin_email}")
        return admin_user


user_service = UserService()
