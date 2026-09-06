import logging
from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.models.base import Base
# Import all models to guarantee registration
from app.models import User, Item, Claim, Notification, AuditLog
from app.services.user_service import user_service
from app.services.audit_service import audit_service

logger = logging.getLogger("unifound.init_db")


def init_db(db: Session) -> None:
    """Create database tables and securely seed initial administrator if applicable."""
    logger.info("Initializing database schema and metadata...")
    Base.metadata.create_all(bind=engine)
    
    admin = user_service.ensure_initial_admin(db)
    if admin:
        logger.info(f"Verified administrator presence: {admin.email}")
        audit_service.log(
            db=db,
            action="SYSTEM_INIT",
            entity_type="SYSTEM",
            entity_id=admin.id,
            actor_id=admin.id,
            details="Database schema initialized and admin verified.",
        )
    logger.info("Database initialization completed successfully.")


def init() -> None:
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()


if __name__ == "__main__":
    init()
