from enum import Enum
from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
    text,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.item import Item


class ClaimStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(
        ForeignKey("items.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    claimant_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ClaimStatus] = mapped_column(
        SQLEnum(ClaimStatus),
        default=ClaimStatus.PENDING,
        nullable=False,
        index=True,
    )
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
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

    # Relationships
    item: Mapped["Item"] = relationship(
        "Item",
        back_populates="claims",
        foreign_keys=[item_id],
    )
    claimant: Mapped["User"] = relationship(
        "User",
        back_populates="claims",
        foreign_keys=[claimant_id],
    )
    reviewer: Mapped["User | None"] = relationship(
        "User",
        back_populates="reviewed_claims",
        foreign_keys=[reviewed_by],
    )

    __table_args__ = (
        Index(
            "uq_active_claim_per_user_item",
            "item_id",
            "claimant_id",
            unique=True,
            sqlite_where=text("status = 'PENDING'"),
            postgresql_where=text("status = 'PENDING'"),
        ),
        Index("ix_claims_item_status", "item_id", "status"),
        Index("ix_claims_claimant_status", "claimant_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Claim id={self.id} item_id={self.item_id} claimant_id={self.claimant_id} status={self.status}>"
