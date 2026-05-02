from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.usuario import Usuario
from app.models.audit import AuditLog
from app.core.dependencies import get_current_user, require_role
from app.schemas.audit import AuditLogResponse

router = APIRouter()

@router.get("/log", response_model=List[AuditLogResponse])
async def get_audit_log(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "SUPER_ADMIN", "DIRECTIVA"]))
) -> Any:
    """
    Retorna los registros de auditoría para el tenant actual.
    """
    result = await db.execute(
        select(AuditLog)
        .filter(AuditLog.tenant_id == current_user.tenant_id)
        .order_by(AuditLog.created_at.desc())
        .limit(100)
    )
    return result.scalars().all()
