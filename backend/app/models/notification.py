from enum import Enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class NotificationType(str, Enum):
    INFO = "INFO"
    MATCH_ALERT = "MATCH_ALERT"
    CLAIM_UPDATE = "CLAIM_UPDATE"
    SYSTEM = "SYSTEM"


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[NotificationType] = mapped_column(
        SQLEnum(NotificationType),
        default=NotificationType.INFO,
        nullable=False,
        index=True,
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="notifications",
        foreign_keys=[user_id],
    )

    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "is_read"),
    )

    def __repr__(self) -> str:
        return f"<Notification id={self.id} user_id={self.user_id} title={self.title} is_read={self.is_read}>"
