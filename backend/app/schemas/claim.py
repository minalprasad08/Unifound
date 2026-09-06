from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from app.models.claim import ClaimStatus


class ClaimBase(BaseModel):
    item_id: int
    description: str = Field(..., min_length=10, description="Detailed explanation of item ownership")
    evidence: Optional[str] = Field(None, description="Identifying marks, serial numbers, purchase receipt notes, etc.")


class ClaimCreate(ClaimBase):
    pass


class ClaimUpdate(BaseModel):
    description: Optional[str] = Field(None, min_length=10)
    evidence: Optional[str] = None


class ClaimReviewAction(BaseModel):
    admin_notes: Optional[str] = Field(None, description="Optional administrative notes or reason for decision")


class ClaimReview(BaseModel):
    status: ClaimStatus
    admin_notes: Optional[str] = None


class ClaimItemInfo(BaseModel):
    id: int
    title: str
    item_type: str
    category: str
    location: str
    incident_date: datetime
    image_url: Optional[str] = None
    status: str
    reported_by: int

    model_config = {
        "from_attributes": True
    }


class ClaimUserInfo(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    department: Optional[str] = None
    student_id: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class ClaimResponse(ClaimBase):
    id: int
    claimant_id: int
    status: ClaimStatus
    admin_notes: Optional[str] = None
    reviewed_by: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    item: Optional[ClaimItemInfo] = None
    claimant: Optional[ClaimUserInfo] = None

    model_config = {
        "from_attributes": True
    }


class AdminClaimsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    claims: List[ClaimResponse]
