from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.usuario import Usuario
from app.models.movimiento import Movimiento, CategoriaMovimiento
from app.core.dependencies import get_current_user
from pydantic import BaseModel
from datetime import date

router = APIRouter()

# Schemas
class CategoriaResponse(BaseModel):
    id: Any
    nombre: str
    tipo: str
    color: Optional[str]

class MovimientoCreate(BaseModel):
    tipo: str # 'ingreso', 'egreso'
    monto: int
    fecha: date
    descripcion: str
    categoria_id: Optional[Any] = None
    forma_pago: Optional[str] = "transferencia"

class MovimientoResponse(BaseModel):
    id: Any
    tipo: str
    monto: int
    fecha: date
    descripcion: str
    anulado: bool

@router.get("/categorias", response_model=List[CategoriaResponse])
async def list_categorias(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(CategoriaMovimiento).filter(CategoriaMovimiento.tenant_id == current_user.tenant_id)
    )
    return result.scalars().all()

@router.get("/", response_model=List[MovimientoResponse])
async def list_movimientos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(Movimiento)
        .filter(Movimiento.tenant_id == current_user.tenant_id)
        .order_by(Movimiento.fecha.desc())
    )
    return result.scalars().all()

@router.post("/", response_model=MovimientoResponse)
async def create_movimiento(
    mov_in: MovimientoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    new_mov = Movimiento(
        tenant_id=current_user.tenant_id,
        registrado_por=current_user.id,
        **mov_in.model_dump()
    )
    db.add(new_mov)
    await db.commit()
    await db.refresh(new_mov)
    return new_mov

@router.get("/saldo")
async def get_saldo(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Calculate current balance for the tenant.
    """
    # Sum ingresos
    ingresos_result = await db.execute(
        select(func.sum(Movimiento.monto))
        .filter(Movimiento.tenant_id == current_user.tenant_id, Movimiento.tipo == 'ingreso', Movimiento.anulado == False)
    )
    ingresos = ingresos_result.scalar() or 0
    
    # Sum egresos
    egresos_result = await db.execute(
        select(func.sum(Movimiento.monto))
        .filter(Movimiento.tenant_id == current_user.tenant_id, Movimiento.tipo == 'egreso', Movimiento.anulado == False)
    )
    egresos = egresos_result.scalar() or 0
    
    return {"saldo": ingresos - egresos}
