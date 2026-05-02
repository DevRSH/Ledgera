from fastapi import APIRouter
from app.api.v1 import auth, alumnos, movimientos, public, cuotas, documentos

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(alumnos.router, prefix="/alumnos", tags=["alumnos"])
api_router.include_router(movimientos.router, prefix="/movimientos", tags=["movimientos"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(cuotas.router, prefix="/cuotas", tags=["cuotas"])
api_router.include_router(documentos.router, prefix="/documentos", tags=["documentos"])

