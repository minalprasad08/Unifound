from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ImageAnalysisResult(BaseModel):
    item_type: Optional[str] = Field(None, description="Detected object or item type")
    colors: List[str] = Field(default_factory=list, description="Dominant visual colors")
    brand: Optional[str] = Field(None, description="Detected manufacturer or brand name")
    visible_text: List[str] = Field(default_factory=list, description="Visible text or markings")
    characteristics: List[str] = Field(default_factory=list, description="Visual physical traits")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Visual detection confidence score (0.0 to 1.0)")
    analyzer: str = Field(..., description="Name/identifier of the visual analyzer model")
    analyzed_at: datetime = Field(..., description="Timestamp of visual inspection")

    model_config = {
        "from_attributes": True
    }


class ImageAnalysisResponse(BaseModel):
    item_id: int
    image_url: str
    image_analysis: ImageAnalysisResult
