import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.item import ItemType, ItemStatus
from app.models.user import UserRole
from app.schemas.claim import ClaimCreate
from app.services.item_service import item_service
from app.services.claim_service import claim_service
from app.services.matching_service import matching_service
from app.services.image_analysis_service import image_analysis_service
from app.services.audit_service import audit_service
from app.mcp.context import get_current_mcp_user, mcp_db_session, MCPAuthError, MCPForbiddenError

logger = logging.getLogger("unifound.mcp.tools")


def _get_db(db: Optional[Session] = None) -> tuple[Session, bool]:
    """Return database session and whether caller owns session lifecycle."""
    if db is not None:
        return db, False
    context_sess = mcp_db_session.get()
    if context_sess is not None:
        return context_sess, False
    return SessionLocal(), True


def mcp_search_items(
    keyword: Optional[str] = None,
    item_type: Optional[str] = None,
    category: Optional[str] = None,
    location: Optional[str] = None,
    status: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db_session: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Search lost and found items using parameterized database queries via the service layer.
    Agents never execute direct database queries.
    """
    db, owns_session = _get_db(db_session)
    try:
        current_user = get_current_mcp_user(db)

        # Parse enums and dates
        parsed_type = None
        if item_type:
            try:
                parsed_type = ItemType(item_type.upper())
            except ValueError:
                return {"error": f"Invalid item_type '{item_type}'. Must be 'LOST' or 'FOUND'.", "code": "VALIDATION_ERROR"}

        parsed_status = None
        if status:
            try:
                parsed_status = ItemStatus(status.upper())
            except ValueError:
                return {"error": f"Invalid status '{status}'.", "code": "VALIDATION_ERROR"}

        dt_from = None
        if from_date:
            try:
                dt_from = datetime.fromisoformat(from_date.replace("Z", "+00:00"))
            except ValueError:
                return {"error": "Invalid from_date ISO format.", "code": "VALIDATION_ERROR"}

        dt_to = None
        if to_date:
            try:
                dt_to = datetime.fromisoformat(to_date.replace("Z", "+00:00"))
            except ValueError:
                return {"error": "Invalid to_date ISO format.", "code": "VALIDATION_ERROR"}

        total, items = item_service.search_items(
            db=db,
            keyword=keyword,
            item_type=parsed_type,
            category=category,
            location=location,
            status=parsed_status,
            from_date=dt_from,
            to_date=dt_to,
            sort_by="created_at",
            sort_order="desc",
            page=page,
            page_size=page_size,
        )

        audit_service.log(
            db=db,
            action="MCP_TOOL_EXECUTION",
            entity_type="ITEM",
            actor_id=current_user.id,
            details=f"search_items(keyword='{keyword}', total={total})",
        )

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [
                {
                    "id": it.id,
                    "item_type": it.item_type.value,
                    "title": it.title,
                    "description": it.description,
                    "category": it.category,
                    "location": it.location,
                    "incident_date": it.incident_date.isoformat(),
                    "status": it.status.value,
                    "image_url": it.image_url,
                    "image_analysis": it.image_analysis,
                    "created_at": it.created_at.isoformat(),
                }
                for it in items
            ],
        }
    except (MCPAuthError, MCPForbiddenError) as e:
        return {"error": str(e), "code": "AUTH_ERROR"}
    except Exception as e:
        logger.error("mcp_search_items failed: %s", e)
        return {"error": "Internal error searching items.", "code": "INTERNAL_ERROR"}
    finally:
        if owns_session:
            db.close()


def mcp_get_item(
    item_id: int,
    db_session: Optional[Session] = None,
) -> Dict[str, Any]:
    """Retrieve item details safely without exposing sensitive reporter fields."""
    db, owns_session = _get_db(db_session)
    try:
        current_user = get_current_mcp_user(db)
        item = item_service.get_by_id(db, item_id)
        if not item:
            return {"error": f"Item with ID {item_id} not found.", "code": "ITEM_NOT_FOUND"}

        audit_service.log(
            db=db,
            action="MCP_TOOL_EXECUTION",
            entity_type="ITEM",
            entity_id=item.id,
            actor_id=current_user.id,
            details=f"get_item({item_id})",
        )

        return {
            "id": item.id,
            "item_type": item.item_type.value,
            "title": item.title,
            "description": item.description,
            "category": item.category,
            "location": item.location,
            "incident_date": item.incident_date.isoformat(),
            "status": item.status.value,
            "image_url": item.image_url,
            "image_analysis": item.image_analysis,
            "created_at": item.created_at.isoformat(),
            "reported_by_name": item.reporter.full_name if item.reporter else "Anonymous",
        }
    except (MCPAuthError, MCPForbiddenError) as e:
        return {"error": str(e), "code": "AUTH_ERROR"}
    except Exception as e:
        logger.error("mcp_get_item failed: %s", e)
        return {"error": "Internal error retrieving item.", "code": "INTERNAL_ERROR"}
    finally:
        if owns_session:
            db.close()


def mcp_find_matches(
    item_id: int,
    min_confidence: float = 40.0,
    page: int = 1,
    page_size: int = 10,
    db_session: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Find opposite-type potential matches for an item using multi-factor similarity scoring.
    Calls matching_service directly.
    """
    db, owns_session = _get_db(db_session)
    try:
        current_user = get_current_mcp_user(db)
        source = item_service.get_by_id(db, item_id)
        if not source:
            return {"error": f"Source item {item_id} not found.", "code": "ITEM_NOT_FOUND"}

        total, matches = matching_service.find_matches(
            db=db,
            source_item=source,
            min_confidence=min_confidence,
            page=page,
            page_size=page_size,
        )

        audit_service.log(
            db=db,
            action="MCP_TOOL_EXECUTION",
            entity_type="ITEM",
            entity_id=source.id,
            actor_id=current_user.id,
            details=f"find_matches({item_id}, found={total})",
        )

        formatted_matches = []
        for m in matches:
            cand = m["item"]
            formatted_matches.append({
                "item_id": cand.id,
                "item_type": cand.item_type.value,
                "title": cand.title,
                "category": cand.category,
                "location": cand.location,
                "incident_date": cand.incident_date.isoformat(),
                "confidence": m["confidence"],
                "title_score": m.get("title_score"),
                "description_score": m.get("description_score"),
                "category_score": m.get("category_score"),
                "location_score": m.get("location_score"),
                "date_score": m.get("date_score"),
                "visual_score": m.get("visual_score"),
                "visual_evidence": m.get("visual_evidence", []),
                "explanation": m.get("explanation"),
            })

        return {
            "source_item_id": source.id,
            "source_item_title": source.title,
            "source_item_type": source.item_type.value,
            "total": total,
            "page": page,
            "page_size": page_size,
            "matches": formatted_matches,
        }
    except (MCPAuthError, MCPForbiddenError) as e:
        return {"error": str(e), "code": "AUTH_ERROR"}
    except Exception as e:
        logger.error("mcp_find_matches failed: %s", e)
        return {"error": "Internal error finding matches.", "code": "INTERNAL_ERROR"}
    finally:
        if owns_session:
            db.close()


def mcp_analyze_image(
    item_id: int,
    db_session: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Extract structured visual attributes from an item's uploaded image.
    Enforces item reporter or administrator authorization.
    """
    db, owns_session = _get_db(db_session)
    try:
        current_user = get_current_mcp_user(db)
        res = image_analysis_service.analyze_item_image(
            db=db,
            item_id=item_id,
            current_user=current_user,
        )

        audit_service.log(
            db=db,
            action="MCP_TOOL_EXECUTION",
            entity_type="ITEM",
            entity_id=item_id,
            actor_id=current_user.id,
            details=f"analyze_image({item_id})",
        )
        return res
    except HTTPException as e:
        return {"error": e.detail, "code": f"HTTP_{e.status_code}"}
    except (MCPAuthError, MCPForbiddenError) as e:
        return {"error": str(e), "code": "AUTH_ERROR"}
    except Exception as e:
        logger.error("mcp_analyze_image failed: %s", e)
        return {"error": "Image analysis encountered an error.", "code": "INTERNAL_ERROR"}
    finally:
        if owns_session:
            db.close()


def mcp_create_claim(
    item_id: int,
    description: str,
    evidence: Optional[str] = None,
    db_session: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Submit an ownership claim for an item.
    Claimant identity is strictly derived from authenticated MCP context.
    Never trusts claimant ID passed in tool parameters.
    """
    db, owns_session = _get_db(db_session)
    try:
        current_user = get_current_mcp_user(db)

        if len(description.strip()) < 10:
            return {"error": "Description must be at least 10 characters.", "code": "VALIDATION_ERROR"}

        claim_in = ClaimCreate(
            item_id=item_id,
            description=description.strip(),
            evidence=evidence.strip() if evidence else None,
        )

        claim = claim_service.create(
            db=db,
            claim_in=claim_in,
            claimant_id=current_user.id,
        )

        audit_service.log(
            db=db,
            action="MCP_TOOL_EXECUTION",
            entity_type="CLAIM",
            entity_id=claim.id,
            actor_id=current_user.id,
            details=f"create_claim for item {item_id}",
        )

        return {
            "claim_id": claim.id,
            "item_id": claim.item_id,
            "claimant_id": claim.claimant_id,
            "status": claim.status.value,
            "description": claim.description,
            "created_at": claim.created_at.isoformat(),
        }
    except HTTPException as e:
        return {"error": e.detail, "code": f"HTTP_{e.status_code}"}
    except (MCPAuthError, MCPForbiddenError) as e:
        return {"error": str(e), "code": "AUTH_ERROR"}
    except Exception as e:
        logger.error("mcp_create_claim failed: %s", e)
        return {"error": f"Claim creation failed: {str(e)}", "code": "INTERNAL_ERROR"}
    finally:
        if owns_session:
            db.close()


def mcp_get_claim_status(
    claim_id: int,
    db_session: Optional[Session] = None,
) -> Dict[str, Any]:
    """
    Retrieve status and details of an ownership claim.
    Requires caller to be claimant, item reporter, or admin.
    """
    db, owns_session = _get_db(db_session)
    try:
        current_user = get_current_mcp_user(db)
        claim = claim_service.get_by_id(db, claim_id)
        if not claim:
            return {"error": f"Claim {claim_id} not found.", "code": "CLAIM_NOT_FOUND"}

        # Authorization: claimant, item reporter, or admin
        is_claimant = claim.claimant_id == current_user.id
        is_reporter = claim.item and claim.item.reported_by == current_user.id
        is_admin = current_user.role == UserRole.ADMIN

        if not (is_claimant or is_reporter or is_admin):
            return {
                "error": "You are not authorized to view this claim.",
                "code": "FORBIDDEN",
            }

        audit_service.log(
            db=db,
            action="MCP_TOOL_EXECUTION",
            entity_type="CLAIM",
            entity_id=claim.id,
            actor_id=current_user.id,
            details=f"get_claim_status({claim_id})",
        )

        return {
            "claim_id": claim.id,
            "item_id": claim.item_id,
            "item_title": claim.item.title if claim.item else None,
            "claimant_id": claim.claimant_id,
            "status": claim.status.value,
            "description": claim.description,
            "evidence": claim.evidence,
            "admin_notes": claim.admin_notes if (is_admin or is_claimant) else None,
            "created_at": claim.created_at.isoformat(),
            "updated_at": claim.updated_at.isoformat(),
        }
    except (MCPAuthError, MCPForbiddenError) as e:
        return {"error": str(e), "code": "AUTH_ERROR"}
    except Exception as e:
        logger.error("mcp_get_claim_status failed: %s", e)
        return {"error": "Internal error retrieving claim status.", "code": "INTERNAL_ERROR"}
    finally:
        if owns_session:
            db.close()
