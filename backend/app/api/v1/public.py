import uuid
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.models.movimiento import Movimiento
from app.models.comprobante import ComprobantePago
from app.schemas.comprobante import VerificacionPublicaResponse
from app.services import movimiento_service

router = APIRouter()

@router.get("/{tenant_id}/saldo")
async def get_public_saldo(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Obtiene el saldo público de un curso (sin PII).
    """
    saldo = await movimiento_service.calcular_saldo_actual(db, tenant_id)
    return {"saldo": saldo}

@router.get("/{tenant_id}/movimientos")
async def get_public_movimientos(
    tenant_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Lista movimientos recientes para transparencia pública, ocultando datos sensibles.
    """
    result = await db.execute(
        select(Movimiento)
        .filter(Movimiento.tenant_id == tenant_id, Movimiento.anulado == False)
        .order_by(Movimiento.fecha.desc())
        .limit(20)
    )
    movs = result.scalars().all()
    
    # Sanitización explícita: Solo devolvemos campos no sensibles
    return [
        {
            "fecha": m.fecha,
            "tipo": m.tipo,
            "monto": m.monto,
            "descripcion": m.descripcion, # La descripción debe ser general (ej: "Pago mensual")
            "categoria_id": m.categoria_id
        } for m in movs
    ]

@router.get("/verify/{folio}", response_model=VerificacionPublicaResponse)
async def verificar_comprobante(
    folio: str, 
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Endpoint para verificación vía QR. NUNCA devuelve PII (nombres, RUTs).
    """
    result = await db.execute(
        select(ComprobantePago).filter(
            ComprobantePago.folio == folio
        )
    )
    comp = result.scalars().first()
    
    if not comp:
        return {"valido": False, "motivo": "Comprobante no encontrado"}
    
    if comp.anulado:
        return {
            "valido": False, 
            "folio": comp.folio,
            "motivo": f"Este comprobante fue ANULADO el {comp.anulado_at.strftime('%d/%m/%Y')}"
        }
    
    return {
        "valido": True,
        "folio": comp.folio,
        "concepto": f"Pago de Cuota {comp.mes}/{comp.año}",
        "monto": comp.monto,
        "fecha_pago": comp.fecha_pago
    }
