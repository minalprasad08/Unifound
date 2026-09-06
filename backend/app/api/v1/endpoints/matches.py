from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.item import Item
from app.schemas.match import ItemMatchesResponse
from app.services.matching_service import matching_service

router = APIRouter()


@router.get("/item/{item_id}", response_model=ItemMatchesResponse)
def get_item_matches(
    item_id: int,
    min_confidence: float = Query(default=0.0, ge=0.0, le=100.0, description="Minimum confidence threshold"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=10, ge=1, le=50, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Retrieve ranked potential candidate matches for the specified item.
    - Compares LOST <-> FOUND exclusively.
    - Filters out CLOSED/RESOLVED candidates and the item itself.
    - Returns explainable similarity scores and rank order by confidence.
    """
    source_item = db.get(Item, item_id)
    if not source_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} does not exist.",
        )

    total, matches = matching_service.find_matches(
        db=db,
        source_item=source_item,
        min_confidence=min_confidence,
        page=page,
        page_size=page_size,
    )

    return {
        "source_item_id": source_item.id,
        "source_item_title": source_item.title,
        "source_item_type": source_item.item_type.value,
        "total": total,
        "page": page,
        "page_size": page_size,
        "matches": matches,
    }
