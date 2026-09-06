from datetime import datetime, timezone, timedelta
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.models.item import ItemType, ItemStatus


class ItemBase(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: str = Field(..., min_length=5)
    category: str = Field(..., min_length=2, max_length=100)
    location: str = Field(..., min_length=2, max_length=255)
    incident_date: datetime
    image_url: Optional[str] = Field(None, max_length=500)

    @field_validator("incident_date")
    def validate_incident_date(cls, v: datetime) -> datetime:
        # Prevent reporting incident dates in the future (allowing max 1 day buffer for timezones)
        now = datetime.now(timezone.utc)
        v_tz = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        if v_tz > now + timedelta(days=1):
            raise ValueError("Incident date cannot be in the future.")
        return v


class ItemReportCreate(ItemBase):
    """Payload for POST /items/lost and POST /items/found (item_type inferred from endpoint)."""
    pass


class ItemCreate(ItemBase):
    item_type: ItemType


class ItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = Field(None, min_length=5)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    location: Optional[str] = Field(None, min_length=2, max_length=255)
    incident_date: Optional[datetime] = None
    image_url: Optional[str] = None
    status: Optional[ItemStatus] = None

    @field_validator("incident_date")
    def validate_incident_date(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is None:
            return v
        now = datetime.now(timezone.utc)
        v_tz = v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        if v_tz > now + timedelta(days=1):
            raise ValueError("Incident date cannot be in the future.")
        return v


class ItemReporterInfo(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class ItemResponse(ItemBase):
    id: int
    item_type: ItemType
    status: ItemStatus
    reported_by: int
    image_analysis: Optional[dict] = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class ItemDetailResponse(ItemResponse):
    reporter: Optional[ItemReporterInfo] = None

    model_config = {
        "from_attributes": True
    }


class ItemSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[ItemResponse]

