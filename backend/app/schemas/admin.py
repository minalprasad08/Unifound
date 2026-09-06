from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel


class RecentActivityItem(BaseModel):
    id: int
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    actor_id: Optional[int] = None
    details: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class AdminStatsResponse(BaseModel):
    total_users: int
    total_items: int
    items_by_type: Dict[str, int]
    items_by_status: Dict[str, int]
    pending_claims: int
    total_claims: int
    recent_activity: List[RecentActivityItem]
