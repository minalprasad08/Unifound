from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
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



LANDING_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UniFound - AI-Powered Lost &amp; Found Portal</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #07090e;
      --card-bg: rgba(17, 24, 39, 0.85);
      --card-border: rgba(255, 255, 255, 0.1);
      --primary: #6366f1;
      --primary-glow: rgba(99, 102, 241, 0.35);
      --accent: #a855f7;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --success: #10b981;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #07090e 70%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px;
      line-height: 1.5;
    }
    .container {
      max-width: 820px;
      width: 100%;
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: 24px;
      padding: 40px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 80px var(--primary-glow);
    }
    .badge-row {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 20px;
    }
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #34d399;
      padding: 6px 14px;
      border-radius: 9999px;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      background: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 10px #10b981;
      animation: pulse 2s infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.4; transform: scale(0.85); }
    }
    h1 {
      font-size: 34px;
      font-weight: 800;
      background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 50%, #94a3b8 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 10px;
      letter-spacing: -0.5px;
    }
    p.lead {
      color: var(--text-muted);
      font-size: 15px;
      margin-bottom: 32px;
      max-width: 680px;
    }
    .cards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }
    .card {
      background: rgba(255, 255, 255, 0.03);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.25s ease;
      color: inherit;
    }
    .card:hover {
      background: rgba(255, 255, 255, 0.06);
      border-color: rgba(99, 102, 241, 0.4);
      transform: translateY(-3px);
      box-shadow: 0 12px 24px -10px rgba(99, 102, 241, 0.25);
    }
    .card.primary-card {
      background: linear-gradient(135deg, rgba(99, 102, 241, 0.18) 0%, rgba(168, 85, 247, 0.18) 100%);
      border-color: rgba(168, 85, 247, 0.35);
      grid-column: 1 / -1;
    }
    .card.primary-card:hover {
      border-color: rgba(168, 85, 247, 0.6);
      box-shadow: 0 16px 32px -10px rgba(168, 85, 247, 0.35);
    }
    .card-icon {
      font-size: 26px;
      margin-bottom: 10px;
    }
    .card h3 {
      font-size: 17px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    .card p {
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.45;
      margin-bottom: 16px;
    }
    .badge-pill {
      font-size: 11px;
      padding: 3px 8px;
      border-radius: 999px;
      background: rgba(168, 85, 247, 0.2);
      border: 1px solid rgba(168, 85, 247, 0.4);
      color: #d8b4fe;
    }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      font-weight: 600;
      font-size: 14px;
      padding: 10px 18px;
      border-radius: 10px;
      text-decoration: none;
      transition: all 0.2s;
      width: fit-content;
    }
    .btn-gradient {
      background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
      color: #fff;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
    }
    .btn-gradient:hover {
      opacity: 0.95;
      box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }
    .btn-glass {
      background: rgba(255, 255, 255, 0.08);
      color: #e2e8f0;
      border: 1px solid rgba(255, 255, 255, 0.12);
    }
    .btn-glass:hover {
      background: rgba(255, 255, 255, 0.15);
      color: #fff;
    }
    .meta-bar {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      padding-top: 24px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 12.5px;
      color: #64748b;
      gap: 12px;
    }
    .meta-bar strong {
      color: #94a3b8;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="badge-row">
      <div class="status-badge">
        <span class="pulse-dot"></span>
        API Live (Render Cloud)
      </div>
      <span style="color:#64748b; font-size:13px;">FastAPI &bull; Python 3.11</span>
    </div>

    <h1>UniFound Portal</h1>
    <p class="lead">Production REST API backend for campus-wide Lost &amp; Found management with automated multi-factor AI matching, secure claim verification, and Model Context Protocol (MCP) agents.</p>

    <div class="cards-grid">
      <div class="card primary-card">
        <div>
          <div class="card-icon">🚀</div>
          <h3>UniFound Web Application <span class="badge-pill">Vercel Live</span></h3>
          <p>Access the responsive user interface to report lost or found items, view matches, and submit verification claims.</p>
        </div>
        <a href="https://unifound-app.vercel.app" target="_blank" rel="noopener" class="btn btn-gradient">
          Launch Web Application &rarr;
        </a>
      </div>

      <div class="card">
        <div>
          <div class="card-icon">⚡</div>
          <h3>Swagger Docs</h3>
          <p>Interactive API playground to execute endpoints, inspect models, and test OAuth2 tokens.</p>
        </div>
        <a href="/docs" class="btn btn-glass">Open /docs</a>
      </div>

      <div class="card">
        <div>
          <div class="card-icon">📖</div>
          <h3>ReDoc Specs</h3>
          <p>Structured OpenAPI specification reference for backend integrations.</p>
        </div>
        <a href="/redoc" class="btn btn-glass">Open /redoc</a>
      </div>

      <div class="card">
        <div>
          <div class="card-icon">🩺</div>
          <h3>Health Heartbeat</h3>
          <p>Real-time monitor checking database connection and service responsiveness.</p>
        </div>
        <a href="/health" class="btn btn-glass">Check /health</a>
      </div>
    </div>

    <div class="meta-bar">
      <div>Parul University &bull; Faculty of IT &amp; Computer Science</div>
      <div>Project Guide: <strong>Mrs. Arpita Meet Vaidya</strong></div>
    </div>
  </div>
</body>
</html>"""


@app.get("/")
def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return HTMLResponse(content=LANDING_HTML)
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": "/docs",
        "frontend": "https://unifound-app.vercel.app",
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

