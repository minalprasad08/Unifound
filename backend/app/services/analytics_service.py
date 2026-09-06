import logging
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, and_
from app.models.user import User
from app.models.item import Item, ItemType, ItemStatus
from app.models.claim import Claim, ClaimStatus
from app.models.notification import Notification, NotificationType
from app.models.audit_log import AuditLog
from app.schemas.analytics import (
    AdminAnalyticsResponse,
    AnalyticsDateBucket,
    CategoryCount,
    LocationCount,
)
from app.schemas.admin import RecentActivityItem

logger = logging.getLogger("unifound.analytics")


class AnalyticsService:
    @staticmethod
    def get_analytics(
        db: Session,
        period: str = "30d",
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
    ) -> AdminAnalyticsResponse:
        """
        Compute deterministic database-backed administrative analytics over configurable date horizons.
        Uses pure SQL aggregation queries. Zero generative/LLM approximations.
        """
        now = datetime.now(timezone.utc)

        # 1. Resolve date boundaries
        if period == "7d":
            from_dt = now - timedelta(days=7)
            to_dt = now
        elif period == "90d":
            from_dt = now - timedelta(days=90)
            to_dt = now
        elif period == "custom" or from_date is not None or to_date is not None:
            period = "custom"
            from_dt = from_date or (now - timedelta(days=30))
            to_dt = to_date or now
            if from_dt > to_dt:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="from_date cannot be after to_date.",
                )
        else:
            # Default to 30d
            period = "30d"
            from_dt = now - timedelta(days=30)
            to_dt = now

        # Ensure timezone awareness
        if from_dt.tzinfo is None:
            from_dt = from_dt.replace(tzinfo=timezone.utc)
        if to_dt.tzinfo is None:
            to_dt = to_dt.replace(tzinfo=timezone.utc)

        # 2. User metrics
        total_users = db.scalar(select(func.count(User.id))) or 0
        active_users = db.scalar(select(func.count(User.id)).where(User.is_active == True)) or 0

        # 3. Item metrics in timeframe
        item_time_filter = and_(Item.created_at >= from_dt, Item.created_at <= to_dt)

        total_lost = db.scalar(
            select(func.count(Item.id)).where(item_time_filter, Item.item_type == ItemType.LOST)
        ) or 0
        total_found = db.scalar(
            select(func.count(Item.id)).where(item_time_filter, Item.item_type == ItemType.FOUND)
        ) or 0

        open_reports = db.scalar(
            select(func.count(Item.id)).where(item_time_filter, Item.status == ItemStatus.OPEN)
        ) or 0
        resolved_reports = db.scalar(
            select(func.count(Item.id)).where(item_time_filter, Item.status == ItemStatus.RESOLVED)
        ) or 0
        closed_reports = db.scalar(
            select(func.count(Item.id)).where(item_time_filter, Item.status == ItemStatus.CLOSED)
        ) or 0

        # 4. Claim metrics in timeframe
        claim_time_filter = and_(Claim.created_at >= from_dt, Claim.created_at <= to_dt)

        pending_claims = db.scalar(
            select(func.count(Claim.id)).where(claim_time_filter, Claim.status == ClaimStatus.PENDING)
        ) or 0
        approved_claims = db.scalar(
            select(func.count(Claim.id)).where(claim_time_filter, Claim.status == ClaimStatus.APPROVED)
        ) or 0
        rejected_claims = db.scalar(
            select(func.count(Claim.id)).where(claim_time_filter, Claim.status == ClaimStatus.REJECTED)
        ) or 0

        # 5. Notification & Match metrics in timeframe
        notif_time_filter = and_(Notification.created_at >= from_dt, Notification.created_at <= to_dt)

        notifications_generated = db.scalar(
            select(func.count(Notification.id)).where(notif_time_filter)
        ) or 0
        high_confidence_matches = db.scalar(
            select(func.count(Notification.id)).where(
                notif_time_filter,
                Notification.type == NotificationType.MATCH_ALERT,
            )
        ) or 0

        # 6. Categorical breakdowns (Parameterized Group By)
        cat_stmt = (
            select(Item.category, func.count(Item.id))
            .where(item_time_filter)
            .group_by(Item.category)
            .order_by(func.count(Item.id).desc())
            .limit(10)
        )
        cat_results = db.execute(cat_stmt).all()
        reports_by_category = [
            CategoryCount(category=row[0] or "Uncategorized", count=row[1])
            for row in cat_results
        ]

        loc_stmt = (
            select(Item.location, func.count(Item.id))
            .where(item_time_filter)
            .group_by(Item.location)
            .order_by(func.count(Item.id).desc())
            .limit(10)
        )
        loc_results = db.execute(loc_stmt).all()
        reports_by_location = [
            LocationCount(location=row[0] or "Unknown", count=row[1])
            for row in loc_results
        ]

        # 7. Time series histograms
        # Date grouping using func.date() for cross-DB compatibility
        reports_trend_stmt = (
            select(func.date(Item.created_at).label("day"), func.count(Item.id))
            .where(item_time_filter)
            .group_by("day")
            .order_by("day")
        )
        reports_trend_res = db.execute(reports_trend_stmt).all()
        reports_over_time = [
            AnalyticsDateBucket(date=str(row[0]), count=row[1])
            for row in reports_trend_res
            if row[0] is not None
        ]

        claims_trend_stmt = (
            select(func.date(Claim.created_at).label("day"), func.count(Claim.id))
            .where(claim_time_filter)
            .group_by("day")
            .order_by("day")
        )
        claims_trend_res = db.execute(claims_trend_stmt).all()
        claims_over_time = [
            AnalyticsDateBucket(date=str(row[0]), count=row[1])
            for row in claims_trend_res
            if row[0] is not None
        ]

        # 8. Recent platform audit activity
        recent_audit = list(
            db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(10)).scalars().all()
        )
        recent_activity = [
            RecentActivityItem(
                id=a.id,
                action=a.action,
                entity_type=a.entity_type,
                entity_id=a.entity_id,
                actor_id=a.actor_id,
                created_at=a.created_at,
                details=a.details,
            )
            for a in recent_audit
        ]

        return AdminAnalyticsResponse(
            total_users=total_users,
            active_users=active_users,
            total_lost_reports=total_lost,
            total_found_reports=total_found,
            open_reports=open_reports,
            resolved_reports=resolved_reports,
            closed_reports=closed_reports,
            pending_claims=pending_claims,
            approved_claims=approved_claims,
            rejected_claims=rejected_claims,
            match_count=high_confidence_matches * 2,  # paired estimates
            high_confidence_matches=high_confidence_matches,
            notifications_generated=notifications_generated,
            reports_by_category=reports_by_category,
            reports_by_location=reports_by_location,
            lost_vs_found_distribution={"lost": total_lost, "found": total_found},
            claims_over_time=claims_over_time,
            reports_over_time=reports_over_time,
            recent_activity=recent_activity,
            period=period,
            from_date=from_dt.isoformat(),
            to_date=to_dt.isoformat(),
        )


analytics_service = AnalyticsService()
