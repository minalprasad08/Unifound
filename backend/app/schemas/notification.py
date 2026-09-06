from datetime import datetime
from pydantic import BaseModel, Field
from app.models.notification import NotificationType


class NotificationBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    message: str = Field(..., min_length=2)
    type: NotificationType = NotificationType.INFO


class NotificationCreate(NotificationBase):
    user_id: int


class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
