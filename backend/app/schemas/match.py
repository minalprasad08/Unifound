from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.item import ItemResponse


class ItemMatchCandidate(BaseModel):
    item: ItemResponse
    confidence: float = Field(..., description="Overall confidence score normalized from 0.0 to 100.0")
    title_score: float = Field(..., description="Title similarity score from 0.0 to 1.0")
    description_score: float = Field(..., description="Description similarity score from 0.0 to 1.0")
    category_score: float = Field(..., description="Category similarity score from 0.0 to 1.0")
    location_score: float = Field(..., description="Location similarity score from 0.0 to 1.0")
    date_score: float = Field(..., description="Incident date proximity score from 0.0 to 1.0")
    visual_score: Optional[float] = Field(None, description="Visual similarity score from 0.0 to 1.0 when image analysis is present")
    visual_evidence: List[str] = Field(default_factory=list, description="Extracted visual evidence bullet points")
    explanation: str = Field(..., description="Explainable match breakdown and confidence rationale")


class ItemMatchesResponse(BaseModel):
    source_item_id: int
    source_item_title: str
    source_item_type: str
    total: int
    page: int
    page_size: int
    matches: List[ItemMatchCandidate]
