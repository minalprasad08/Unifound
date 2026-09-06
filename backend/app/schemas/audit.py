from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AuditLogBase(BaseModel):
    action: str = Field(..., max_length=100)
    entity_type: str = Field(..., max_length=50)
    entity_id: Optional[int] = None
    details: Optional[str] = None


class AuditLogCreate(AuditLogBase):
    actor_id: Optional[int] = None


class AuditLogResponse(AuditLogBase):
    id: int
    actor_id: Optional[int] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }
