import uuid
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from fastapi import HTTPException, status

from app.models.movimiento import Movimiento
from app.models.usuario import Usuario
from app.services import audit_service

async def crear_movimiento(db: AsyncSession, tenant_id: uuid.UUID, actor: Usuario, data: dict) -> Movimiento:
    """
    Crea un nuevo movimiento (ingreso/egreso) y registra el evento en auditoría.
    """
    nuevo_movimiento = Movimiento(
        tenant_id=tenant_id,
        tipo=data['tipo'],
        monto=data['monto'],
        fecha=data.get('fecha', datetime.utcnow().date()),
        descripcion=data['descripcion'],
        categoria_id=data.get('categoria_id'),
        forma_pago=data.get('forma_pago', 'efectivo'),
        referencia_bancaria=data.get('referencia_bancaria'),
        registrado_por=actor.id
    )
    
    db.add(nuevo_movimiento)
    await db.flush() # Para obtener el ID del movimiento
    
    # Auditoría
    await audit_service.registrar_evento(
        db,
        tenant_id=tenant_id,
        actor_id=actor.id,
        actor_email=actor.email,
        accion=audit_service.CREATE_MOVIMIENTO,
        entidad="Movimiento",
        entidad_id=str(nuevo_movimiento.id),
        payload_despues=data
    )
    
    return nuevo_movimiento

async def anular_movimiento(db: AsyncSession, tenant_id: uuid.UUID, actor: Usuario, movimiento_id: uuid.UUID, motivo: str) -> Movimiento:
    """
    Anula un movimiento existente. Solo permitido para el rol DIRECTIVA o SUPER_ADMIN.
    """
    # Validación de Rol (Directiva o Super Admin)
    if actor.rol not in ['DIRECTIVA', 'SUPER_ADMIN']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo la Directiva o el Administrador pueden anular movimientos."
        )
    
    stmt = select(Movimiento).filter(Movimiento.id == movimiento_id, Movimiento.tenant_id == tenant_id)
    result = await db.execute(stmt)
    movimiento = result.scalars().first()
    
    if not movimiento:
        raise HTTPException(status_code=404, detail="Movimiento no encontrado.")
    
    if movimiento.anulado:
        raise HTTPException(status_code=400, detail="El movimiento ya se encuentra anulado.")

    payload_antes = {
        "anulado": movimiento.anulado,
        "monto": movimiento.monto,
        "descripcion": movimiento.descripcion
    }

    # Marcado de anulación
    movimiento.anulado = True
    movimiento.anulado_por = actor.id
    movimiento.anulado_at = datetime.utcnow()
    movimiento.motivo_anulacion = motivo
    
    # Auditoría
    await audit_service.registrar_evento(
        db,
        tenant_id=tenant_id,
        actor_id=actor.id,
        actor_email=actor.email,
        accion=audit_service.ANULAR_MOVIMIENTO,
        entidad="Movimiento",
        entidad_id=str(movimiento.id),
        payload_antes=payload_antes,
        payload_despues={"anulado": True, "motivo": motivo}
    )
    
    return movimiento

async def calcular_saldo_actual(db: AsyncSession, tenant_id: uuid.UUID) -> int:
    """
    Calcula el saldo real actual: SUM(ingresos) - SUM(egresos), excluyendo anulados.
    Retorna entero CLP.
    """
    # Suma de Ingresos
    stmt_ingresos = select(func.sum(Movimiento.monto)).filter(
        Movimiento.tenant_id == tenant_id,
        Movimiento.tipo == 'ingreso',
        Movimiento.anulado == False
    )
    # Suma de Egresos
    stmt_egresos = select(func.sum(Movimiento.monto)).filter(
        Movimiento.tenant_id == tenant_id,
        Movimiento.tipo == 'egreso',
        Movimiento.anulado == False
    )
    
    res_i = await db.execute(stmt_ingresos)
    res_e = await db.execute(stmt_egresos)
    
    ingresos = res_i.scalar() or 0
    egresos = res_e.scalar() or 0
    
    return int(ingresos - egresos)

async def obtener_resumen_mensual(db: AsyncSession, tenant_id: uuid.UUID, año: int) -> List[Dict[str, Any]]:
    """
    Obtiene el resumen financiero de los 12 meses de un año específico.
    """
    resumen = []
    
    for mes in range(1, 13):
        # Filtro base para el mes
        base_filter = and_(
            Movimiento.tenant_id == tenant_id,
            extract('year', Movimiento.fecha) == año,
            extract('month', Movimiento.fecha) == mes,
            Movimiento.anulado == False
        )
        
        # Ingresos del mes
        stmt_i = select(func.sum(Movimiento.monto)).filter(base_filter, Movimiento.tipo == 'ingreso')
        # Egresos del mes
        stmt_e = select(func.sum(Movimiento.monto)).filter(base_filter, Movimiento.tipo == 'egreso')
        
        res_i = await db.execute(stmt_i)
        res_e = await db.execute(stmt_e)
        
        ingresos = res_i.scalar() or 0
        egresos = res_e.scalar() or 0
        
        resumen.append({
            "mes": mes,
            "ingresos": int(ingresos),
            "egresos": int(egresos),
            "saldo_periodo": int(ingresos - egresos)
        })
        
    return resumen
