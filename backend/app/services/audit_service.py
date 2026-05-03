import uuid
from typing import Optional, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.models.audit import AuditLog

# Acciones estándar
CREATE_MOVIMIENTO = "CREATE_MOVIMIENTO"
UPDATE_MOVIMIENTO = "UPDATE_MOVIMIENTO"
ANULAR_MOVIMIENTO = "ANULAR_MOVIMIENTO"
CREATE_ALUMNO = "CREATE_ALUMNO"
UPDATE_ALUMNO = "UPDATE_ALUMNO"
DELETE_ALUMNO = "DELETE_ALUMNO"
REGISTRAR_PAGO = "REGISTRAR_PAGO"
ANULAR_COMPROBANTE = "ANULAR_COMPROBANTE"
EMITIR_VALE = "EMITIR_VALE"
LOGIN_EXITOSO = "LOGIN_EXITOSO"
LOGIN_FALLIDO = "LOGIN_FALLIDO"
CAMBIO_ROL = "CAMBIO_ROL"

async def registrar_evento(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    actor_id: Optional[uuid.UUID],
    actor_email: str,
    accion: str,
    entidad: Optional[str] = None,
    entidad_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    payload_antes: Optional[dict] = None,
    payload_despues: Optional[dict] = None
) -> None:
    """
    Registra un evento en el log de auditoría.
    Solo realiza INSERT. No hace commit propio (el caller controla la transacción).
    """
    log_entry = AuditLog(
        tenant_id=tenant_id,
        usuario_id=actor_id,
        accion=accion,
        entidad_tipo=entidad,
        entidad_id=entidad_id,
        payload_antes=jsonable_encoder(payload_antes) if payload_antes else None,
        payload_despues=jsonable_encoder(payload_despues) if payload_despues else None,
        ip_address=ip_address,
        user_agent=None,
        created_at=datetime.now(timezone.utc)
    )
    
    db.add(log_entry)
    # No se hace commit aquí, se delega al caller.
    await db.flush()
