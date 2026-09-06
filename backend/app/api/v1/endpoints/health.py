from datetime import datetime, timezone
from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.deps import get_db
from app.core.config import settings

router = APIRouter()


@router.get("", response_model=Dict[str, Any])
@router.get("/", response_model=Dict[str, Any])
def health_check(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Health check endpoint to verify system and database connectivity."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
