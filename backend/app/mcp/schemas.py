from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# 1. search_items
class SearchItemsInput(BaseModel):
    keyword: Optional[str] = Field(None, description="Search term matching item title or description")
    item_type: Optional[str] = Field(None, description="Filter by item type: 'LOST' or 'FOUND'")
    category: Optional[str] = Field(None, description="Filter by category (e.g. 'Electronics', 'Books')")
    location: Optional[str] = Field(None, description="Filter by campus location or building")
    status: Optional[str] = Field(None, description="Filter by status: 'OPEN', 'CLAIM_PENDING', 'CLAIMED', 'RESOLVED', 'CLOSED'")
    from_date: Optional[str] = Field(None, description="Filter incidents from ISO datetime (inclusive)")
    to_date: Optional[str] = Field(None, description="Filter incidents up to ISO datetime (inclusive)")
    page: int = Field(1, ge=1, description="Page number starting from 1")
    page_size: int = Field(10, ge=1, le=100, description="Number of results per page (max 100)")


# 2. get_item
class GetItemInput(BaseModel):
    item_id: int = Field(..., description="Unique ID of the item report to retrieve")


# 3. find_matches
class FindMatchesInput(BaseModel):
    item_id: int = Field(..., description="ID of the item report to find opposite-type candidate matches for")
    min_confidence: float = Field(40.0, ge=0.0, le=100.0, description="Minimum confidence score threshold (0.0 to 100.0)")
    page: int = Field(1, ge=1, description="Results page number")
    page_size: int = Field(10, ge=1, le=50, description="Max matches to return per page")


# 4. analyze_image
class AnalyzeImageInput(BaseModel):
    item_id: int = Field(..., description="ID of the item with an uploaded image to analyze")


# 5. create_claim
class CreateClaimInput(BaseModel):
    item_id: int = Field(..., description="ID of the item report to submit a claim for")
    description: str = Field(..., min_length=10, max_length=1000, description="Detailed explanation of ownership (min 10 characters)")
    evidence: Optional[str] = Field(None, max_length=1000, description="Supporting evidence such as serial numbers, markings, or receipts")


# 6. get_claim_status
class GetClaimStatusInput(BaseModel):
    claim_id: int = Field(..., description="ID of the claim to inspect")


# Tool Response wrappers
class ToolExecutionError(BaseModel):
    error: str = Field(..., description="Error message describing what failed")
    code: str = Field(..., description="Machine-readable error code")
    details: Optional[Dict[str, Any]] = None
