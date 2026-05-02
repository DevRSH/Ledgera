from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.core.database import get_db
from app.models.usuario import Usuario
from app.models.cuota import ConfiguracionCuota, PagoCuota, Condonacion
from app.core.dependencies import get_current_user
from pydantic import BaseModel
from datetime import date

router = APIRouter()

# Schemas
class CuotaConfigCreate(BaseModel):
    año: int
    mes: int
    monto: int
    descripcion: Optional[str] = None
    fecha_vencimiento: Optional[date] = None

class PagoCuotaCreate(BaseModel):
    alumno_id: Any
    año: int
    mes: int
    monto_pagado: int
    fecha_pago: date
    observaciones: Optional[str] = None

@router.get("/config")
async def get_config(
    año: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(ConfiguracionCuota)
        .filter(ConfiguracionCuota.tenant_id == current_user.tenant_id, ConfiguracionCuota.año == año)
    )
    return result.scalars().all()

@router.post("/config")
async def set_config(
    configs: List[CuotaConfigCreate],
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    for cfg in configs:
        new_cfg = ConfiguracionCuota(
            tenant_id=current_user.tenant_id,
            **cfg.model_dump()
        )
        db.add(new_cfg)
    await db.commit()
    return {"message": "Configuración guardada"}

@router.post("/pago")
async def registrar_pago(
    pago_in: PagoCuotaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Register a student fee payment.
    """
    # Check if already paid
    existing = await db.execute(
        select(PagoCuota).filter(
            PagoCuota.tenant_id == current_user.tenant_id,
            PagoCuota.alumno_id == pago_in.alumno_id,
            PagoCuota.año == pago_in.año,
            PagoCuota.mes == pago_in.mes
        )
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="El mes ya está pagado para este alumno")
    
    new_pago = PagoCuota(
        tenant_id=current_user.tenant_id,
        registrado_por=current_user.id,
        **pago_in.model_dump()
    )
    db.add(new_pago)
    
    # Optional: Automatically create a Movimiento record here if needed
    # (Simplified for now as per sprint requirement)
    
    await db.commit()
    return {"message": "Pago registrado"}

@router.get("/estado/{alumno_id}")
async def get_estado_deuda(
    alumno_id: Any,
    año: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Calculate debt status for a student.
    """
    # Get configured months
    config_res = await db.execute(
        select(ConfiguracionCuota).filter(ConfiguracionCuota.tenant_id == current_user.tenant_id, ConfiguracionCuota.año == año)
    )
    configs = config_res.scalars().all()
    
    # Get paid months
    pagos_res = await db.execute(
        select(PagoCuota).filter(PagoCuota.alumno_id == alumno_id, PagoCuota.año == año)
    )
    pagos = {p.mes: p for p in pagos_res.scalars().all()}
    
    # Get condoned months
    cond_res = await db.execute(
        select(Condonacion).filter(Condonacion.alumno_id == alumno_id, Condonacion.año == año)
    )
    conds = {c.mes: c for c in cond_res.scalars().all() if c.mes is not None}
    condonado_anual = any(c.mes is None for c in cond_res.scalars().all())

    meses_adeudados = []
    total_deuda = 0
    
    for cfg in configs:
        if condonado_anual or cfg.mes in conds or cfg.mes in pagos:
            continue
        meses_adeudados.append(cfg.mes)
        total_deuda += cfg.monto
        
    return {
        "meses_pagados": list(pagos.keys()),
        "meses_adeudados": meses_adeudados,
        "monto_adeudado": total_deuda,
        "al_dia": len(meses_adeudados) == 0
    }
