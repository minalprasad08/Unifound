from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from app.schemas.admin import RecentActivityItem


class AnalyticsDateBucket(BaseModel):
    date: str
    count: int


class CategoryCount(BaseModel):
    category: str
    count: int


class LocationCount(BaseModel):
    location: str
    count: int


class AdminAnalyticsResponse(BaseModel):
    total_users: int = Field(..., description="Total registered platform users")
    active_users: int = Field(..., description="Total active non-deactivated users")
    total_lost_reports: int = Field(..., description="Total LOST reports submitted in period")
    total_found_reports: int = Field(..., description="Total FOUND reports submitted in period")
    open_reports: int = Field(..., description="Currently open reports in period")
    resolved_reports: int = Field(..., description="Resolved reports in period")
    closed_reports: int = Field(..., description="Closed reports in period")
    pending_claims: int = Field(..., description="Claims awaiting administrative review in period")
    approved_claims: int = Field(..., description="Approved claims in period")
    rejected_claims: int = Field(..., description="Rejected claims in period")
    match_count: int = Field(..., description="Total evaluated potential matches in period")
    high_confidence_matches: int = Field(..., description="High-confidence (>=70%) match candidates")
    notifications_generated: int = Field(..., description="Total event notifications generated in period")
    reports_by_category: List[CategoryCount] = Field(default_factory=list)
    reports_by_location: List[LocationCount] = Field(default_factory=list)
    lost_vs_found_distribution: Dict[str, int] = Field(default_factory=dict)
    claims_over_time: List[AnalyticsDateBucket] = Field(default_factory=list)
    reports_over_time: List[AnalyticsDateBucket] = Field(default_factory=list)
    recent_activity: List[RecentActivityItem] = Field(default_factory=list)
    period: str
    from_date: Optional[str] = None
    to_date: Optional[str] = None

    model_config = {
        "from_attributes": True
    }
