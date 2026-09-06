from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func
from app.models.notification import Notification, NotificationType
from app.schemas.notification import NotificationCreate


class NotificationService:
    @staticmethod
    def create(db: Session, notification_in: NotificationCreate) -> Notification:
        notification = Notification(
            user_id=notification_in.user_id,
            title=notification_in.title.strip(),
            message=notification_in.message.strip(),
            type=notification_in.type,
            is_read=False,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def list_for_user(
        db: Session,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> List[Notification]:
        stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            stmt = stmt.where(Notification.is_read == False)
        
        stmt = stmt.order_by(Notification.created_at.desc())
        
        if page is not None and page_size is not None:
            offset = max(0, (page - 1) * page_size)
            stmt = stmt.offset(offset).limit(page_size)
        else:
            stmt = stmt.limit(limit)

        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def list_for_user_paginated(
        db: Session,
        user_id: int,
        unread_only: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[int, int, List[Notification]]:
        """Returns (total_count, unread_count, paginated_items) for authenticated user."""
        base_stmt = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            base_stmt = base_stmt.where(Notification.is_read == False)

        total = db.scalar(select(func.count()).select_from(base_stmt.subquery())) or 0
        unread_count = db.scalar(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id,
                Notification.is_read == False,
            )
        ) or 0

        offset = max(0, (page - 1) * page_size)
        stmt = base_stmt.order_by(Notification.created_at.desc()).offset(offset).limit(page_size)
        items = list(db.execute(stmt).scalars().all())
        return total, unread_count, items

    @staticmethod
    def notify_match_alert(
        db: Session,
        user_id: int,
        source_title: str,
        matched_title: str,
        matched_location: str,
        confidence: float,
        item_id: int,
        match_item_id: int,
    ) -> Notification:
        """Create a standardized high-confidence match alert notification."""
        title = f"Potential Match Alert ({confidence:.0f}% confidence)"
        message = (
            f"We found a potential match for '{source_title}': "
            f"'{matched_title}' at {matched_location} (Confidence: {confidence:.0f}%)."
        )
        return NotificationService.create(
            db=db,
            notification_in=NotificationCreate(
                user_id=user_id,
                title=title,
                message=message,
                type=NotificationType.MATCH_ALERT,
            ),
        )

    @staticmethod
    def mark_as_read(db: Session, notification_id: int, user_id: int) -> Optional[Notification]:
        notification = db.get(Notification, notification_id)
        if not notification or notification.user_id != user_id:
            return None
        notification.is_read = True
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read == False)
            .values(is_read=True)
        )
        result = db.execute(stmt)
        db.commit()
        return result.rowcount


notification_service = NotificationService()


