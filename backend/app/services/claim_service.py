from datetime import datetime, timezone
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func
from app.models.claim import Claim, ClaimStatus
from app.models.item import Item, ItemStatus
from app.models.notification import NotificationType
from app.schemas.claim import ClaimCreate
from app.schemas.notification import NotificationCreate
from app.services.notification_service import notification_service
from app.services.audit_service import audit_service


class ClaimValidationError(HTTPException, ValueError):
    def __init__(self, status_code: int, detail: str):
        HTTPException.__init__(self, status_code=status_code, detail=detail)
        ValueError.__init__(self, detail)


class ClaimService:
    @staticmethod
    def get_by_id(db: Session, claim_id: int) -> Optional[Claim]:
        stmt = (
            select(Claim)
            .where(Claim.id == claim_id)
            .options(
                joinedload(Claim.item),
                joinedload(Claim.claimant),
                joinedload(Claim.reviewer),
            )
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def get_active_claim(db: Session, item_id: int, claimant_id: int) -> Optional[Claim]:
        """Check for an existing PENDING claim by the same user on the specified item."""
        stmt = select(Claim).where(
            Claim.item_id == item_id,
            Claim.claimant_id == claimant_id,
            Claim.status == ClaimStatus.PENDING,
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_by_item(db: Session, item_id: int) -> List[Claim]:
        stmt = (
            select(Claim)
            .where(Claim.item_id == item_id)
            .options(
                joinedload(Claim.item),
                joinedload(Claim.claimant),
            )
            .order_by(Claim.created_at.desc())
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def list_by_claimant(db: Session, claimant_id: int) -> List[Claim]:
        stmt = (
            select(Claim)
            .where(Claim.claimant_id == claimant_id)
            .options(
                joinedload(Claim.item),
                joinedload(Claim.claimant),
            )
            .order_by(Claim.created_at.desc())
        )
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def list_admin_claims(
        db: Session,
        status_filter: Optional[ClaimStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[int, List[Claim]]:
        count_stmt = select(func.count(Claim.id))
        if status_filter:
            count_stmt = count_stmt.where(Claim.status == status_filter)
        total = db.scalar(count_stmt) or 0

        data_stmt = (
            select(Claim)
            .options(
                joinedload(Claim.item),
                joinedload(Claim.claimant),
                joinedload(Claim.reviewer),
            )
        )
        if status_filter:
            data_stmt = data_stmt.where(Claim.status == status_filter)

        offset = (page - 1) * page_size
        data_stmt = data_stmt.order_by(Claim.created_at.desc()).offset(offset).limit(page_size)
        claims = list(db.execute(data_stmt).scalars().all())
        return total, claims

    @staticmethod
    def create(db: Session, claim_in: ClaimCreate, claimant_id: int) -> Claim:
        item = db.get(Item, claim_in.item_id)
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target item does not exist.",
            )

        # Rule: Cannot claim own item
        if item.reported_by == claimant_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot claim an item you reported yourself.",
            )

        # Rule: Cannot claim CLOSED, RESOLVED, or CLAIMED items
        if item.status in (ItemStatus.CLAIMED, ItemStatus.RESOLVED, ItemStatus.CLOSED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot claim an item with status {item.status.value}.",
            )

        # Rule: One active pending claim per user + item
        existing_active = ClaimService.get_active_claim(db, item_id=claim_in.item_id, claimant_id=claimant_id)
        if existing_active:
            raise ClaimValidationError(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have an active pending claim on this item.",
            )

        claim = Claim(
            item_id=claim_in.item_id,
            claimant_id=claimant_id,
            description=claim_in.description.strip(),
            evidence=claim_in.evidence.strip() if claim_in.evidence else None,
            status=ClaimStatus.PENDING,
        )
        db.add(claim)

        # Transition item to CLAIM_PENDING if currently OPEN
        if item.status == ItemStatus.OPEN:
            item.status = ItemStatus.CLAIM_PENDING
            db.add(item)

        db.commit()
        db.refresh(claim)

        # Notifications
        notification_service.create(
            db,
            NotificationCreate(
                user_id=claimant_id,
                title="Claim Submitted",
                message=f"Your claim for '{item.title}' has been submitted and is pending review.",
                type=NotificationType.CLAIM_UPDATE,
            ),
        )

        notification_service.create(
            db,
            NotificationCreate(
                user_id=item.reported_by,
                title="New Claim Filed",
                message=f"A campus member has submitted an ownership claim for your reported item '{item.title}'.",
                type=NotificationType.MATCH_ALERT,
            ),
        )

        # Audit Log
        audit_service.log(
            db=db,
            action="CLAIM_CREATED",
            entity_type="CLAIM",
            entity_id=claim.id,
            actor_id=claimant_id,
            details=f"Claim #{claim.id} submitted for item #{item.id} ('{item.title}')",
        )

        return ClaimService.get_by_id(db, claim.id) or claim

    @staticmethod
    def cancel(db: Session, claim_id: int, user_id: int) -> Claim:
        claim = ClaimService.get_by_id(db, claim_id)
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Claim not found.",
            )

        if claim.claimant_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to cancel this claim.",
            )

        if claim.status != ClaimStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending claims can be cancelled.",
            )

        claim.status = ClaimStatus.CANCELLED
        db.add(claim)

        item = claim.item
        if item:
            # Check if there are other pending claims
            other_pending = db.execute(
                select(Claim).where(
                    Claim.item_id == item.id,
                    Claim.id != claim.id,
                    Claim.status == ClaimStatus.PENDING,
                )
            ).scalars().first()
            if not other_pending and item.status == ItemStatus.CLAIM_PENDING:
                item.status = ItemStatus.OPEN
                db.add(item)

        db.commit()
        db.refresh(claim)

        # Notification to claimant
        notification_service.create(
            db,
            NotificationCreate(
                user_id=user_id,
                title="Claim Cancelled",
                message=f"You cancelled your claim for '{item.title if item else 'item'}'.",
                type=NotificationType.CLAIM_UPDATE,
            ),
        )

        # Audit Log
        audit_service.log(
            db=db,
            action="CLAIM_CANCELLED",
            entity_type="CLAIM",
            entity_id=claim.id,
            actor_id=user_id,
            details=f"Claim #{claim.id} cancelled by claimant",
        )

        return claim

    @staticmethod
    def review(
        db: Session,
        claim: Claim,
        new_status: ClaimStatus,
        admin_notes: Optional[str],
        reviewer_id: int,
    ) -> Claim:
        if claim.status != ClaimStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only pending claims can be reviewed.",
            )

        if new_status not in (ClaimStatus.APPROVED, ClaimStatus.REJECTED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Review decision must be either APPROVED or REJECTED.",
            )

        claim.status = new_status
        claim.admin_notes = admin_notes
        claim.reviewed_by = reviewer_id
        claim.reviewed_at = datetime.now(timezone.utc)
        db.add(claim)

        item = claim.item
        if item:
            if new_status == ClaimStatus.APPROVED:
                item.status = ItemStatus.CLAIMED
                db.add(item)

                # Automatically reject any other pending claims on this item
                other_pending = db.execute(
                    select(Claim).where(
                        Claim.item_id == item.id,
                        Claim.id != claim.id,
                        Claim.status == ClaimStatus.PENDING,
                    )
                ).scalars().all()

                for other in other_pending:
                    other.status = ClaimStatus.REJECTED
                    other.admin_notes = "Another ownership claim was verified and approved by administration."
                    other.reviewed_by = reviewer_id
                    other.reviewed_at = datetime.now(timezone.utc)
                    db.add(other)

                    notification_service.create(
                        db,
                        NotificationCreate(
                            user_id=other.claimant_id,
                            title="Claim Closed",
                            message=f"Your claim for '{item.title}' was closed as another verified claim was approved.",
                            type=NotificationType.CLAIM_UPDATE,
                        ),
                    )

                # Notifications for approval
                notification_service.create(
                    db,
                    NotificationCreate(
                        user_id=claim.claimant_id,
                        title="Claim Approved!",
                        message=f"Your ownership claim for '{item.title}' has been approved by campus security.",
                        type=NotificationType.CLAIM_UPDATE,
                    ),
                )

                notification_service.create(
                    db,
                    NotificationCreate(
                        user_id=item.reported_by,
                        title="Item Claimed",
                        message=f"An ownership claim for your reported item '{item.title}' was verified and approved.",
                        type=NotificationType.CLAIM_UPDATE,
                    ),
                )

                audit_service.log(
                    db=db,
                    action="CLAIM_APPROVED",
                    entity_type="CLAIM",
                    entity_id=claim.id,
                    actor_id=reviewer_id,
                    details=f"Admin #{reviewer_id} approved claim #{claim.id}",
                )

                audit_service.log(
                    db=db,
                    action="ITEM_CLAIM_STATUS_CHANGED",
                    entity_type="ITEM",
                    entity_id=item.id,
                    actor_id=reviewer_id,
                    details=f"Item #{item.id} status transitioned to CLAIMED",
                )

            elif new_status == ClaimStatus.REJECTED:
                # Check if there are other pending claims
                other_pending = db.execute(
                    select(Claim).where(
                        Claim.item_id == item.id,
                        Claim.id != claim.id,
                        Claim.status == ClaimStatus.PENDING,
                    )
                ).scalars().first()

                if not other_pending and item.status == ItemStatus.CLAIM_PENDING:
                    item.status = ItemStatus.OPEN
                    db.add(item)

                # Notification for rejection
                note_suffix = f" Admin note: {admin_notes}" if admin_notes else ""
                notification_service.create(
                    db,
                    NotificationCreate(
                        user_id=claim.claimant_id,
                        title="Claim Rejected",
                        message=f"Your claim for '{item.title}' was reviewed and rejected.{note_suffix}",
                        type=NotificationType.CLAIM_UPDATE,
                    ),
                )

                audit_service.log(
                    db=db,
                    action="CLAIM_REJECTED",
                    entity_type="CLAIM",
                    entity_id=claim.id,
                    actor_id=reviewer_id,
                    details=f"Admin #{reviewer_id} rejected claim #{claim.id}",
                )

        db.commit()
        db.refresh(claim)
        return ClaimService.get_by_id(db, claim.id) or claim


claim_service = ClaimService()
