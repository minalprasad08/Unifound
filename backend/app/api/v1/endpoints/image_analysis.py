import logging
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user
from app.services.image_analysis_service import image_analysis_service
from app.schemas.image_analysis import ImageAnalysisResponse

logger = logging.getLogger("unifound.image_analysis")
router = APIRouter()


@router.post(
    "/{item_id}/analyze-image",
    response_model=ImageAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze item image visual attributes",
)
def analyze_item_image(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Extract structured visual attributes (item type, colors, brand, visible text,
    characteristics, confidence) from an item's uploaded image.
    Requires item reporter or admin authorization.
    """
    return image_analysis_service.analyze_item_image(
        db=db,
        item_id=item_id,
        current_user=current_user,
    )
