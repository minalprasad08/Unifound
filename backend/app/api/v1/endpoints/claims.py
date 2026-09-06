from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_db
from app.models.user import User, UserRole
from app.schemas.claim import ClaimCreate, ClaimResponse
from app.services.claim_service import claim_service
from app.core.rate_limiter import rate_limit_claim

router = APIRouter()


@router.post(
    "/",
    response_model=ClaimResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit_claim)],
)
def submit_claim(
    claim_in: ClaimCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Submit an ownership claim for a lost or found item."""
    claim = claim_service.create(
        db=db,
        claim_in=claim_in,
        claimant_id=current_user.id,
    )
    return claim


@router.get("/my", response_model=List[ClaimResponse])
def get_my_claims(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve all claims submitted by the currently authenticated user."""
    claims = claim_service.list_by_claimant(db=db, claimant_id=current_user.id)
    return claims


@router.get("/{claim_id}", response_model=ClaimResponse)
def get_claim_details(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Retrieve claim details. Accessible by the claimant or an administrator."""
    claim = claim_service.get_by_id(db=db, claim_id=claim_id)
    if not claim:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Claim not found.",
        )
    if claim.claimant_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this claim.",
        )
    return claim


@router.put("/{claim_id}/cancel", response_model=ClaimResponse)
def cancel_my_claim(
    claim_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Cancel a pending claim submitted by the current user."""
    cancelled = claim_service.cancel(db=db, claim_id=claim_id, user_id=current_user.id)
    return cancelled
