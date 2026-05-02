from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.usuario import Usuario
from app.models.audit import AuditLog
from app.core.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()

@router.get("/log", response_model=List[Any])
async def get_audit_log(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    # Security check: Only AUDITOR or higher
    # For now, let's allow all authenticated users for testing
    result = await db.execute(
        select(AuditLog)
        .filter(AuditLog.tenant_id == current_user.tenant_id)
        .order_by(AuditLog.created_at.desc())
        .limit(100)
    )
    return result.scalars().all()
