from datetime import datetime
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.item import ItemType, ItemStatus
from app.schemas.item import (
    ItemReportCreate,
    ItemResponse,
    ItemDetailResponse,
    ItemUpdate,
    ItemSearchResponse,
)
from app.services.item_service import item_service
from app.services.storage_service import storage_service
from app.core.rate_limiter import rate_limit_upload

router = APIRouter()


@router.post("/lost", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def report_lost_item(
    report_in: ItemReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create a new Lost item report."""
    item = item_service.create_report(
        db=db,
        report_in=report_in,
        item_type=ItemType.LOST,
        reporter_id=current_user.id,
    )
    return item


@router.post("/found", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def report_found_item(
    report_in: ItemReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Create a new Found item report."""
    item = item_service.create_report(
        db=db,
        report_in=report_in,
        item_type=ItemType.FOUND,
        reporter_id=current_user.id,
    )
    return item


@router.get("/my", response_model=List[ItemResponse])
def get_my_reports(
    item_type: Optional[ItemType] = None,
    status_filter: Optional[ItemStatus] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve all reports created by the currently authenticated user."""
    items = item_service.list_by_reporter(
        db=db,
        reporter_id=current_user.id,
        item_type=item_type,
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    return items


@router.get("/search", response_model=ItemSearchResponse)
def search_items(
    q: Optional[str] = Query(None, description="Search keyword matching title or description"),
    item_type: Optional[ItemType] = Query(None, description="Filter by LOST or FOUND"),
    category: Optional[str] = Query(None, description="Filter by item category"),
    location: Optional[str] = Query(None, description="Filter by location keyword"),
    status_filter: Optional[ItemStatus] = Query(None, alias="status", description="Filter by status"),
    from_date: Optional[datetime] = Query(None, description="Filter incident date starting from"),
    to_date: Optional[datetime] = Query(None, description="Filter incident date up to"),
    sort_by: str = Query("created_at", pattern="^(created_at|incident_date)$", description="Sort field"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Sort direction"),
    page: int = Query(1, ge=1, description="Page number starting at 1"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page (1-100)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Search and filter lost and found items at the database level.
    Returns paginated items with total count and page metadata.
    """
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="from_date cannot be after to_date",
        )

    total, items = item_service.search_items(
        db=db,
        keyword=q,
        item_type=item_type,
        category=category,
        location=location,
        status=status_filter,
        from_date=from_date,
        to_date=to_date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "items": items,
    }


@router.get("/{item_id}", response_model=ItemDetailResponse)
def get_item_details(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve full details of a specific item report."""
    item = item_service.get_by_id(db, item_id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found.",
        )
    return item


@router.put("/{item_id}", response_model=ItemDetailResponse)
def update_item_report(
    item_id: int,
    item_in: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update an item report. Only the original reporter or an administrator may update."""
    item = item_service.get_by_id(db, item_id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found.",
        )
    updated = item_service.update_item(
        db=db,
        item=item,
        item_in=item_in,
        user=current_user,
    )
    return updated


@router.delete("/{item_id}", response_model=ItemDetailResponse)
def close_item_report(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Close/delete an item report. Only the original reporter or an administrator may close."""
    item = item_service.get_by_id(db, item_id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} not found.",
        )
    closed = item_service.close_item(
        db=db,
        item=item,
        user=current_user,
    )
    return closed


@router.post(
    "/upload-image",
    dependencies=[Depends(rate_limit_upload)],
)
async def upload_item_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> Any:
    """
    Securely upload an item image attachment.
    Enforces format validation, size limit, and path traversal protection.
    """
    image_url = await storage_service.save_image(file)
    return {"image_url": image_url}
