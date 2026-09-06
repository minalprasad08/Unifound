from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that appends production-grade HTTP security headers
    to every HTTP response to mitigate clickjacking, MIME-type sniffing,
    XSS, and unsafe resource embedding.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)

        path = request.url.path
        is_docs = any(path.startswith(p) for p in ["/docs", "/redoc", "/openapi.json", "/api/v1/openapi.json"])

        # 1. Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # 2. Clickjacking protection
        if not is_docs:
            response.headers["X-Frame-Options"] = "DENY"

        # 3. Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 4. Cross-site scripting filter
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # 5. Content Security Policy (exempt docs routes so Swagger UI can load all styles & scripts)
        if not is_docs:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "img-src 'self' data: blob:; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "font-src 'self' data:; "
                "connect-src 'self' http: https:;"
            )

        # 6. Sensitive endpoints: Prevent browser / proxy caching of tokens and administrative data
        if any(sensitive in path for sensitive in ["/auth/", "/admin/", "/agent/"]):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"

        return response
