from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.audit_log import AuditLog
from app.schemas.audit import AuditLogCreate


class AuditService:
    @staticmethod
    def log(
        db: Session,
        action: str,
        entity_type: str,
        entity_id: Optional[int] = None,
        actor_id: Optional[int] = None,
        details: Optional[str] = None,
    ) -> AuditLog:
        log_entry = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            details=details,
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry

    @staticmethod
    def list_logs(
        db: Session,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        actor_id: Optional[int] = None,
        limit: int = 100,
    ) -> List[AuditLog]:
        stmt = select(AuditLog)
        if entity_type:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        if entity_id is not None:
            stmt = stmt.where(AuditLog.entity_id == entity_id)
        if actor_id is not None:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        stmt = stmt.order_by(AuditLog.created_at.desc()).limit(limit)
        return list(db.execute(stmt).scalars().all())


audit_service = AuditService()
