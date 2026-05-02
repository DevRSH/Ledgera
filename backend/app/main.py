from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.core.limiter import limiter
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from contextlib import asynccontextmanager
from app import models  # Force model registration

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

# limiter defined in app.core.limiter

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url="/v1/openapi.json",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None,
    lifespan=lifespan
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    if settings.ENVIRONMENT == "production":
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.FRONTEND_URL.split(",")],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

print(f"DEBUG: Allowed CORS Origins: {[o.strip() for o in settings.FRONTEND_URL.split(',')]} (from {settings.FRONTEND_URL})")

from app.api.v1.router import api_router
app.include_router(api_router, prefix="/v1")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT
    }