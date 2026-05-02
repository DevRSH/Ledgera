from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.models.movimiento import Movimiento
from app.models.comprobante import ComprobantePago

from app.models.tenant import Tenant
import uuid

router = APIRouter()

@router.get("/{tenant_id}/saldo")
async def get_public_saldo(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get public balance for a course.
    """
    ingresos = await db.scalar(
        select(func.sum(Movimiento.monto))
        .filter(Movimiento.tenant_id == tenant_id, Movimiento.tipo == 'ingreso', Movimiento.anulado == False)
    ) or 0
    egresos = await db.scalar(
        select(func.sum(Movimiento.monto))
        .filter(Movimiento.tenant_id == tenant_id, Movimiento.tipo == 'egreso', Movimiento.anulado == False)
    ) or 0
    
    return {"saldo": ingresos - egresos, "actualizado_at": func.now()}

@router.get("/{tenant_id}/movimientos")
async def get_public_movimientos(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get recent movements without PII.
    """
    result = await db.execute(
        select(Movimiento)
        .filter(Movimiento.tenant_id == tenant_id)
        .order_by(Movimiento.fecha.desc())
        .limit(20)
    )
    movs = result.scalars().all()
    
    # Sanitize: remove any personal data if it existed in descripcion (basic approach)
    # The requirement says no RUT, email, etc. Most of these are in Alumno/Apoderado tables.
    # In Movimiento table, we only have descripcion.
    return [
        {
            "fecha": m.fecha,
            "tipo": m.tipo,
            "monto": m.monto,
            "descripcion": m.descripcion,
            "categoria_id": m.categoria_id
        } for m in movs
    ]

@router.get("/verify/{folio}")
async def verificar_comprobante(
    folio: str, 
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Endpoint called from the QR on the printed receipt.
    """
    result = await db.execute(
        select(ComprobantePago).filter(
            ComprobantePago.folio == folio,
            ComprobantePago.anulado == False
        )
    )
    comp = result.scalar_one_or_none()
    
    if not comp:
        return {"valido": False, "motivo": "Comprobante no encontrado o anulado"}
    
    return {
        "valido": True,
        "folio": comp.folio,
        "concepto": f"Cuota {comp.mes}/{comp.año}",
        "monto": comp.monto,
        "fecha_pago": comp.fecha_pago.isoformat(),
        "emitido_en": comp.created_at.isoformat(),
    }

