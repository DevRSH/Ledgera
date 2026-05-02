from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings

print("🚀 Iniciando Ledgera Backend...")
from contextlib import asynccontextmanager
from app.db_init import init_first_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Execute on startup
    await init_first_user()
    yield
    # Execute on shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json" if hasattr(settings, 'API_V1_STR') else "/api/v1/openapi.json",
    lifespan=lifespan
)

print(f"✅ FastAPI configurado. Entorno: {settings.ENVIRONMENT}")
print(f"📡 Intentando escuchar en el puerto configurado por Railway...")


limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "database": "connected",  # Simple placeholder for now
        "project": settings.PROJECT_NAME
    }

# Router inclusion
from app.api.v1.router import api_router
app.include_router(api_router, prefix="/v1")

