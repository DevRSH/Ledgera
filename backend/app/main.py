from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.core.config import settings

print("🚀 Iniciando Ledgera Backend...")
from contextlib import asynccontextmanager
from app.db_init import init_first_user

import subprocess
import sys

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Execute on startup
    print("🛠️ Intentando ejecutar migraciones de base de datos...")
    try:
        # Run alembic migrations as a subprocess to avoid event loop conflicts
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ Migraciones completadas:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error crítico en las migraciones:\n{e.stderr}")
    except Exception as e:
        print(f"❌ Error inesperado al ejecutar alembic: {e}")
        
    try:
        print("👤 Verificando usuario administrador...")
        await init_first_user()
    except Exception as e:
        print(f"⚠️ No se pudo inicializar el usuario: {e}")
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
origins = [settings.FRONTEND_URL] if hasattr(settings, "FRONTEND_URL") and settings.FRONTEND_URL != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

