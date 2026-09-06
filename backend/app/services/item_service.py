import logging
from datetime import datetime
from typing import Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, func, or_
from app.models.item import Item, ItemType, ItemStatus
from app.models.user import User, UserRole
from app.schemas.item import ItemCreate, ItemReportCreate, ItemUpdate
from app.services.audit_service import audit_service

logger = logging.getLogger("unifound.items")

VALID_TRANSITIONS = {
    ItemStatus.OPEN: {ItemStatus.CLAIM_PENDING, ItemStatus.CLOSED},
    ItemStatus.CLAIM_PENDING: {ItemStatus.OPEN, ItemStatus.CLAIMED, ItemStatus.CLOSED},
    ItemStatus.CLAIMED: {ItemStatus.RESOLVED, ItemStatus.CLOSED},
    ItemStatus.RESOLVED: {ItemStatus.CLOSED},
    ItemStatus.CLOSED: set(),
}


class ItemService:
    @staticmethod
    def get_by_id(db: Session, item_id: int) -> Optional[Item]:
        stmt = (
            select(Item)
            .where(Item.id == item_id)
            .options(joinedload(Item.reporter))
        )
        return db.execute(stmt).scalar_one_or_none()

    @staticmethod
    def list_items(
        db: Session,
        item_type: Optional[ItemType] = None,
        category: Optional[str] = None,
        status: Optional[ItemStatus] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Item]:
        stmt = select(Item).options(joinedload(Item.reporter))
        if item_type:
            stmt = stmt.where(Item.item_type == item_type)
        if category:
            stmt = stmt.where(func.lower(Item.category) == category.lower().strip())
        if status:
            stmt = stmt.where(Item.status == status)
        stmt = stmt.order_by(Item.created_at.desc()).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def list_by_reporter(
        db: Session,
        reporter_id: int,
        item_type: Optional[ItemType] = None,
        status: Optional[ItemStatus] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Item]:
        stmt = (
            select(Item)
            .where(Item.reported_by == reporter_id)
            .options(joinedload(Item.reporter))
        )
        if item_type:
            stmt = stmt.where(Item.item_type == item_type)
        if status:
            stmt = stmt.where(Item.status == status)
        stmt = stmt.order_by(Item.created_at.desc()).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    @staticmethod
    def search_items(
        db: Session,
        keyword: Optional[str] = None,
        item_type: Optional[ItemType] = None,
        category: Optional[str] = None,
        location: Optional[str] = None,
        status: Optional[ItemStatus] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[int, List[Item]]:
        """
        Database-level parameterized search and filtering for lost and found items.
        Executes both count and data queries directly at the SQL level.
        """
        conditions = []

        if keyword and keyword.strip():
            kw = keyword.strip()
            conditions.append(
                or_(
                    Item.title.ilike(f"%{kw}%"),
                    Item.description.ilike(f"%{kw}%"),
                )
            )

        if item_type:
            conditions.append(Item.item_type == item_type)

        if category and category.strip():
            conditions.append(func.lower(Item.category) == category.strip().lower())

        if location and location.strip():
            conditions.append(Item.location.ilike(f"%{location.strip()}%"))

        if status:
            conditions.append(Item.status == status)

        if from_date:
            conditions.append(Item.incident_date >= from_date)

        if to_date:
            conditions.append(Item.incident_date <= to_date)

        # 1. Total count query executed at database level
        count_stmt = select(func.count(Item.id))
        if conditions:
            count_stmt = count_stmt.where(*conditions)
        total = db.scalar(count_stmt) or 0

        # 2. Paginated data query executed at database level
        data_stmt = select(Item).options(joinedload(Item.reporter))
        if conditions:
            data_stmt = data_stmt.where(*conditions)

        # Sorting
        sort_column = Item.created_at if sort_by == "created_at" else Item.incident_date
        if sort_order.lower() == "asc":
            data_stmt = data_stmt.order_by(sort_column.asc(), Item.id.asc())
        else:
            data_stmt = data_stmt.order_by(sort_column.desc(), Item.id.desc())

        # Pagination
        offset = (page - 1) * page_size
        data_stmt = data_stmt.offset(offset).limit(page_size)

        items = list(db.execute(data_stmt).scalars().all())
        return total, items

    @staticmethod
    def create_report(
        db: Session,
        report_in: ItemReportCreate,
        item_type: ItemType,
        reporter_id: int,
    ) -> Item:
        item = Item(
            item_type=item_type,
            title=report_in.title.strip(),
            description=report_in.description.strip(),
            category=report_in.category.strip(),
            location=report_in.location.strip(),
            incident_date=report_in.incident_date,
            image_url=report_in.image_url,
            status=ItemStatus.OPEN,
            reported_by=reporter_id,
        )
        db.add(item)
        db.commit()
        db.refresh(item)

        audit_service.log(
            db=db,
            action="ITEM_CREATED",
            entity_type="ITEM",
            entity_id=item.id,
            actor_id=reporter_id,
            details=f"Created {item_type.value} report: '{item.title}' in '{item.category}'",
        )

        # Automatic image analysis hook (non-blocking)
        if item.image_url:
            try:
                from app.services.image_analysis_service import image_analysis_service
                image_analysis_service.auto_analyze_item(db, item)
            except Exception as e:
                logger.warning("Automatic image analysis encountered an error: %s", e)

        # Automatic match detection hook (non-blocking)
        try:
            from app.services.matching_service import matching_service
            matching_service.on_item_created(db, item)
        except Exception as e:
            logger.warning("Automatic match detection encountered an error: %s", e)

        return item

    @staticmethod
    def create(db: Session, item_in: ItemCreate, reported_by: int) -> Item:
        """Backward-compatible create for Phase 1-2 tests."""
        report = ItemReportCreate(
            title=item_in.title,
            description=item_in.description,
            category=item_in.category,
            location=item_in.location,
            incident_date=item_in.incident_date,
            image_url=item_in.image_url,
        )
        return ItemService.create_report(
            db=db,
            report_in=report,
            item_type=item_in.item_type,
            reporter_id=reported_by,
        )

    @staticmethod
    def validate_transition(current_status: ItemStatus, new_status: ItemStatus) -> bool:
        allowed = VALID_TRANSITIONS.get(current_status, set())
        if new_status not in allowed and new_status != current_status:
            raise ValueError(f"Invalid item status transition from {current_status.value} to {new_status.value}")
        return True

    @staticmethod
    def update_item(
        db: Session,
        item: Item,
        item_in: ItemUpdate,
        user: User,
    ) -> Item:
        # Authorization check: only reporter or admin can modify
        if item.reported_by != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to update this item.",
            )

        update_data = item_in.model_dump(exclude_unset=True)

        # Status transition validation
        if "status" in update_data and update_data["status"] != item.status:
            try:
                ItemService.validate_transition(item.status, update_data["status"])
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(e),
                )

        # Disallow tampering with protected fields
        for protected in ["reported_by", "id", "created_at", "item_type"]:
            update_data.pop(protected, None)

        changed_fields = []
        for field, value in update_data.items():
            if getattr(item, field) != value:
                setattr(item, field, value)
                changed_fields.append(field)

        db.add(item)
        db.commit()
        db.refresh(item)

        if changed_fields:
            audit_service.log(
                db=db,
                action="ITEM_UPDATED",
                entity_type="ITEM",
                entity_id=item.id,
                actor_id=user.id,
                details=f"Updated fields: {', '.join(changed_fields)}",
            )
        return item

    @staticmethod
    def update(db: Session, item: Item, item_in: ItemUpdate) -> Item:
        """Backward-compatible update for Phase 2 tests."""
        update_data = item_in.model_dump(exclude_unset=True)
        if "status" in update_data and update_data["status"] != item.status:
            ItemService.validate_transition(item.status, update_data["status"])
        for field, value in update_data.items():
            setattr(item, field, value)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    def close_item(
        db: Session,
        item: Item,
        user: User,
    ) -> Item:
        # Authorization check: only reporter or admin can close
        if item.reported_by != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to close this item.",
            )

        # Validate transition to CLOSED
        try:
            ItemService.validate_transition(item.status, ItemStatus.CLOSED)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )

        item.status = ItemStatus.CLOSED
        db.add(item)
        db.commit()
        db.refresh(item)

        audit_service.log(
            db=db,
            action="ITEM_CLOSED",
            entity_type="ITEM",
            entity_id=item.id,
            actor_id=user.id,
            details=f"Item {item.id} closed by {user.role.value} {user.email}",
        )
        return item

    @staticmethod
    def transition_status(db: Session, item: Item, new_status: ItemStatus) -> Item:
        ItemService.validate_transition(item.status, new_status)
        item.status = new_status
        db.add(item)
        db.commit()
        db.refresh(item)
        return item


item_service = ItemService()
