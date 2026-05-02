import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.usuario import Usuario
from app.models.movimiento import Movimiento, CategoriaMovimiento
from app.schemas.movimiento import (
    MovimientoCreate, MovimientoResponse, MovimientoListResponse,
    AnularMovimientoRequest, MovimientoUpdate
)
from app.services import movimiento_service, audit_service

router = APIRouter()

@router.get("/categorias", response_model=List[Any])
async def list_categorias(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["TESORERO", "DIRECTIVA", "AUDITOR", "SUPER_ADMIN"]))
) -> Any:
    stmt = select(CategoriaMovimiento).filter(CategoriaMovimiento.tenant_id == current_user.tenant_id)
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/", response_model=MovimientoListResponse)
async def list_movimientos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "TESORERO", "DIRECTIVA", "SUPER_ADMIN"])),
    page: int = 1,
    size: int = 50
) -> Any:
    stmt = select(Movimiento).filter(
        Movimiento.tenant_id == current_user.tenant_id
    ).options(joinedload(Movimiento.categoria)).order_by(Movimiento.fecha.desc()).offset((page - 1) * size).limit(size)
    
    total_stmt = select(func.count(Movimiento.id)).filter(Movimiento.tenant_id == current_user.tenant_id)
    total_res = await db.execute(total_stmt)
    total = total_res.scalar() or 0
    
    result = await db.execute(stmt)
    movimientos = result.unique().scalars().all()
    
    return {
        "data": movimientos,
        "total": total,
        "page": page,
        "size": size
    }

@router.post("/", response_model=MovimientoResponse, status_code=status.HTTP_201_CREATED)
async def create_movimiento(
    mov_in: MovimientoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["TESORERO", "SUPER_ADMIN"]))
) -> Any:
    mov = await movimiento_service.crear_movimiento(
        db, 
        tenant_id=current_user.tenant_id,
        actor=current_user,
        data=mov_in.model_dump()
    )
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(Movimiento).filter(Movimiento.id == mov.id).options(joinedload(Movimiento.categoria))
    )
    return result.unique().scalars().first()

@router.post("/{id}/anular", response_model=MovimientoResponse)
async def anular_movimiento(
    id: uuid.UUID,
    body: AnularMovimientoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["DIRECTIVA", "SUPER_ADMIN"]))
) -> Any:
    mov = await movimiento_service.anular_movimiento(
        db,
        tenant_id=current_user.tenant_id,
        actor=current_user,
        movimiento_id=id,
        motivo=body.motivo
    )
    await db.commit()
    
    result = await db.execute(
        select(Movimiento).filter(Movimiento.id == id).options(joinedload(Movimiento.categoria))
    )
    return result.unique().scalars().first()

@router.get("/saldo")
async def get_saldo(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "TESORERO", "DIRECTIVA", "SUPER_ADMIN"]))
) -> Any:
    saldo = await movimiento_service.calcular_saldo_actual(db, current_user.tenant_id)
    return {"saldo": saldo}

@router.get("/resumen-anual")
async def get_resumen_anual(
    año: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "TESORERO", "DIRECTIVA", "SUPER_ADMIN"]))
) -> Any:
    resumen = await movimiento_service.obtener_resumen_mensual(db, current_user.tenant_id, año)
    return resumen
