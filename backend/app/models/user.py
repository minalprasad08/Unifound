from enum import Enum
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from sqlalchemy.sql import func
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.claim import Claim
    from app.models.notification import Notification
    from app.models.audit_log import AuditLog


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    student_id: Mapped[str | None] = mapped_column(String(50), nullable=True, index=True)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole),
        default=UserRole.USER,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Backward compatibility synonym for Phase 1 code
    hashed_password = synonym("password_hash")

    # Relationships with soft-delete/deactivation preference
    items: Mapped[List["Item"]] = relationship(
        "Item",
        back_populates="reporter",
        foreign_keys="Item.reported_by",
    )
    claims: Mapped[List["Claim"]] = relationship(
        "Claim",
        back_populates="claimant",
        foreign_keys="Claim.claimant_id",
    )
    reviewed_claims: Mapped[List["Claim"]] = relationship(
        "Claim",
        back_populates="reviewer",
        foreign_keys="Claim.reviewed_by",
    )
    notifications: Mapped[List["Notification"]] = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Notification.user_id",
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog",
        back_populates="actor",
        foreign_keys="AuditLog.actor_id",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role} is_active={self.is_active}>"
