from fastapi import APIRouter
from app.api.v1.endpoints import auth, users, health, items, claims, admin_claims, notifications, admin, matches, image_analysis, agent

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(items.router, prefix="/items", tags=["Items"])
api_router.include_router(image_analysis.router, prefix="/items", tags=["Image Analysis"])
api_router.include_router(claims.router, prefix="/claims", tags=["Claims"])
api_router.include_router(admin_claims.router, prefix="/admin/claims", tags=["Admin Claims"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin Portal"])
api_router.include_router(matches.router, prefix="/matches", tags=["Matches"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])

