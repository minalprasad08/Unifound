from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.db.session import SessionLocal
from app.db.init_db import init_db
import app.models  # Ensure all models are registered in metadata

logger = setup_logging()

# Ensure uploads directory exists
upload_path = Path(settings.UPLOAD_DIR).resolve()
upload_path.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables and verify administrative state
    logger.info("Initializing database...")
    db = SessionLocal()
    try:
        init_db(db)
    finally:
        db.close()
    yield
    logger.info("Shutting down application...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-grade AI-Powered Lost & Found Management System REST API",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# 1. Production Security Headers Middleware
from app.core.middleware import SecurityHeadersMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(SecurityHeadersMiddleware)

# 2. Trusted Host Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS if settings.ALLOWED_HOSTS else ["*"],
)

# 3. CORS middleware (disallow wildcard credentials)
origins = settings.ALLOWED_ORIGINS
if isinstance(origins, list):
    allowed_origins = origins
else:
    allowed_origins = [origins]

is_wildcard = len(allowed_origins) == 1 and allowed_origins[0] == "*"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["http://localhost:5173"],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=not is_wildcard,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Static file serving for uploaded images
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred. Please contact administrator."},
    )


from app.api.v1.endpoints import auth, users, items, claims, admin_claims, notifications, admin, matches, image_analysis, agent

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Also support direct root routes
app.include_router(auth.router, prefix="/auth", tags=["Auth Direct"])
app.include_router(users.router, prefix="/users", tags=["Users Direct"])
app.include_router(items.router, prefix="/items", tags=["Items Direct"])
app.include_router(image_analysis.router, prefix="/items", tags=["Image Analysis Direct"])
app.include_router(claims.router, prefix="/claims", tags=["Claims Direct"])
app.include_router(admin_claims.router, prefix="/admin/claims", tags=["Admin Claims Direct"])
app.include_router(admin.router, prefix="/admin", tags=["Admin Direct"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications Direct"])
app.include_router(matches.router, prefix="/matches", tags=["Matches Direct"])
app.include_router(agent.router, prefix="/agent", tags=["Agent Direct"])



@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "api_v1": settings.API_V1_STR,
    }


@app.get("/health")
def root_health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }

