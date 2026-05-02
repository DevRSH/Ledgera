from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.usuario import Usuario
from app.models.comunicacion import PlantillaEmail, EmailEnviado
from app.core.dependencies import get_current_user
from pydantic import BaseModel

router = APIRouter()

class PlantillaResponse(BaseModel):
    tipo: str
    asunto_template: str
    activa: bool

@router.get("/plantillas", response_model=List[PlantillaResponse])
async def list_plantillas(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(PlantillaEmail).filter(PlantillaEmail.tenant_id == current_user.tenant_id)
    )
    return result.scalars().all()

@router.get("/historial", response_model=List[Any])
async def get_historial(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(EmailEnviado)
        .filter(EmailEnviado.tenant_id == current_user.tenant_id)
        .order_by(EmailEnviado.created_at.desc())
    )
    return result.scalars().all()
