from fastapi import APIRouter
from app.api.v1 import auth, alumnos, movimientos, public, cuotas, documentos, comunicaciones, reportes, auditoria, conciliacion

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(alumnos.router, prefix="/alumnos", tags=["alumnos"])
api_router.include_router(movimientos.router, prefix="/movimientos", tags=["movimientos"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
api_router.include_router(cuotas.router, prefix="/cuotas", tags=["cuotas"])
api_router.include_router(documentos.router, prefix="/documentos", tags=["documentos"])
api_router.include_router(comunicaciones.router, prefix="/comunicaciones", tags=["comunicaciones"])
api_router.include_router(reportes.router, prefix="/reportes", tags=["reportes"])
api_router.include_router(auditoria.router, prefix="/auditoria", tags=["auditoria"])
api_router.include_router(conciliacion.router, prefix="/conciliacion", tags=["conciliacion"])





