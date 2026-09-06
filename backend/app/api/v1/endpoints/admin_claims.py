from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.api.deps import require_admin, get_db
from app.models.user import User
from app.models.claim import ClaimStatus
from app.schemas.claim import ClaimResponse, ClaimReviewAction, AdminClaimsResponse
from app.services.claim_service import claim_service

router = APIRouter()


@router.get("/", response_model=AdminClaimsResponse)
def list_admin_claims(
    status_filter: Optional[ClaimStatus] = Query(None, alias="status", description="Filter claims by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Retrieve all submitted claims across campus (Administrator only)."""
    total, claims = claim_service.list_admin_claims(
        db=db,
        status_filter=status_filter,
        page=page,
        page_size=page_size,
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "claims": claims,
    }


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_admin_claim_details(
    claim_id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Retrieve full details of a specific claim (Administrator only)."""
    claim = claim_service.get_by_id(db=db, claim_id=claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found.",
        )
    return claim


@router.put("/{claim_id}/approve", response_model=ClaimResponse)
def approve_claim(
    claim_id: int,
    action_in: ClaimReviewAction = ClaimReviewAction(),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Approve an ownership claim and mark target item as CLAIMED (Administrator only)."""
    claim = claim_service.get_by_id(db=db, claim_id=claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found.",
        )
    approved = claim_service.review(
        db=db,
        claim=claim,
        new_status=ClaimStatus.APPROVED,
        admin_notes=action_in.admin_notes,
        reviewer_id=admin_user.id,
    )
    return approved


@router.put("/{claim_id}/reject", response_model=ClaimResponse)
def reject_claim(
    claim_id: int,
    action_in: ClaimReviewAction = ClaimReviewAction(),
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin),
) -> Any:
    """Reject an ownership claim (Administrator only)."""
    claim = claim_service.get_by_id(db=db, claim_id=claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found.",
        )
    rejected = claim_service.review(
        db=db,
        claim=claim,
        new_status=ClaimStatus.REJECTED,
        admin_notes=action_in.admin_notes,
        reviewer_id=admin_user.id,
    )
    return rejected
