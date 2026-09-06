from enum import Enum
from datetime import datetime, timezone
from typing import List, TYPE_CHECKING
from sqlalchemy import (
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.claim import Claim


class ItemType(str, Enum):
    LOST = "LOST"
    FOUND = "FOUND"


class ItemStatus(str, Enum):
    """
    Lifecycle State Machine:
      - OPEN: Item reported and actively searching / available for claims.
      - CLAIM_PENDING: One or more active claims are currently awaiting review.
      - CLAIMED: An ownership claim has been verified and approved by admin.
      - RESOLVED: Item has been physically handed over to the confirmed owner.
      - CLOSED: Item cancelled by reporter or archived/expired by administration.

    Allowed Transitions:
      - OPEN -> CLAIM_PENDING, CLOSED
      - CLAIM_PENDING -> OPEN (if claim rejected/cancelled), CLAIMED, CLOSED
      - CLAIMED -> RESOLVED, CLOSED
      - RESOLVED -> CLOSED (archived)
    """
    OPEN = "OPEN"
    CLAIM_PENDING = "CLAIM_PENDING"
    CLAIMED = "CLAIMED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    item_type: Mapped[ItemType] = mapped_column(
        SQLEnum(ItemType),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    incident_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    image_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)
    status: Mapped[ItemStatus] = mapped_column(
        SQLEnum(ItemStatus),
        default=ItemStatus.OPEN,
        nullable=False,
        index=True,
    )
    reported_by: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
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
    reporter: Mapped["User"] = relationship(
        "User",
        back_populates="items",
        foreign_keys=[reported_by],
    )
    claims: Mapped[List["Claim"]] = relationship(
        "Claim",
        back_populates="item",
        cascade="all, delete-orphan",
        foreign_keys="Claim.item_id",
    )

    __table_args__ = (
        Index("ix_items_type_status", "item_type", "status"),
        Index("ix_items_category_type", "category", "item_type"),
        Index("ix_items_location_date", "location", "incident_date"),
    )

    def __repr__(self) -> str:
        return f"<Item id={self.id} type={self.item_type} title={self.title} status={self.status}>"
