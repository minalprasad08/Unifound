from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.notification import NotificationResponse
from app.services.notification_service import notification_service

router = APIRouter()


@router.get("/my", response_model=List[NotificationResponse])
@router.get("/", response_model=List[NotificationResponse])
def get_user_notifications(
    unread_only: bool = False,
    page: Optional[int] = Query(None, ge=1, description="Page number (1-based)"),
    page_size: Optional[int] = Query(None, ge=1, le=100, description="Items per page"),
    limit: int = Query(50, ge=1, le=100, description="Max notifications to retrieve when unpaginated"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve notifications for the current authenticated user with optional filtering and pagination."""
    notifications = notification_service.list_for_user(
        db=db,
        user_id=current_user.id,
        unread_only=unread_only,
        limit=limit,
        page=page,
        page_size=page_size,
    )
    return notifications



@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Mark an individual notification as read."""
    notification = notification_service.mark_as_read(
        db=db,
        notification_id=notification_id,
        user_id=current_user.id,
    )
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found.",
        )
    return notification


@router.put("/read-all", response_model=dict)
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Mark all unread notifications as read for current user."""
    count = notification_service.mark_all_as_read(db=db, user_id=current_user.id)
    return {"message": "All notifications marked as read", "count": count}
