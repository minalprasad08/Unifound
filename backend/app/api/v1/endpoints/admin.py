from typing import Any, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.api.deps import require_admin, get_db
from app.models.user import User
from app.models.item import Item, ItemType, ItemStatus
from app.models.claim import Claim, ClaimStatus
from app.models.audit_log import AuditLog
from app.schemas.admin import AdminStatsResponse, RecentActivityItem
from app.schemas.analytics import AdminAnalyticsResponse
from app.services.analytics_service import analytics_service
from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_dashboard_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Retrieve comprehensive platform metrics and recent activity (Administrator only)."""
    total_users = db.scalar(select(func.count(User.id))) or 0
    total_items = db.scalar(select(func.count(Item.id))) or 0

    lost_count = db.scalar(select(func.count(Item.id)).where(Item.item_type == ItemType.LOST)) or 0
    found_count = db.scalar(select(func.count(Item.id)).where(Item.item_type == ItemType.FOUND)) or 0

    # Aggregate status counts
    status_counts = {
        "OPEN": db.scalar(select(func.count(Item.id)).where(Item.status == ItemStatus.OPEN)) or 0,
        "CLAIM_PENDING": db.scalar(select(func.count(Item.id)).where(Item.status == ItemStatus.CLAIM_PENDING)) or 0,
        "CLAIMED": db.scalar(select(func.count(Item.id)).where(Item.status == ItemStatus.CLAIMED)) or 0,
        "RESOLVED": db.scalar(select(func.count(Item.id)).where(Item.status == ItemStatus.RESOLVED)) or 0,
        "CLOSED": db.scalar(select(func.count(Item.id)).where(Item.status == ItemStatus.CLOSED)) or 0,
    }

    pending_claims = db.scalar(select(func.count(Claim.id)).where(Claim.status == ClaimStatus.PENDING)) or 0
    total_claims = db.scalar(select(func.count(Claim.id))) or 0

    recent_logs = list(
        db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(10)).scalars().all()
    )

    return {
        "total_users": total_users,
        "total_items": total_items,
        "items_by_type": {
            "LOST": lost_count,
            "FOUND": found_count,
        },
        "items_by_status": status_counts,
        "pending_claims": pending_claims,
        "total_claims": total_claims,
        "recent_activity": recent_logs,
    }


@router.get("/analytics", response_model=AdminAnalyticsResponse)
def get_admin_analytics(
    period: str = Query("30d", pattern="^(7d|30d|90d|custom)$", description="Analytics horizon: 7d, 30d, 90d, custom"),
    from_date: Optional[datetime] = Query(None, description="Custom start date (ISO 8601)"),
    to_date: Optional[datetime] = Query(None, description="Custom end date (ISO 8601)"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Retrieve deep administrative analytics and trends across configurable date ranges (Administrator only)."""
    analytics = analytics_service.get_analytics(
        db=db,
        period=period,
        from_date=from_date,
        to_date=to_date,
    )

    # Audit analytics access
    audit_service.log(
        db=db,
        action="ADMIN_ANALYTICS_VIEWED",
        entity_type="SYSTEM",
        actor_id=admin_user.id,
        details=f"Admin #{admin_user.id} viewed analytics for period={period}",
    )

    return analytics

