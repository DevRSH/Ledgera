import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.services import audit_service
from app.models.audit import AuditLog
from app.models.usuario import Usuario
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_audit_registra_evento_manual(db: AsyncSession):
    tenant_id = uuid.uuid4()
    actor_id = uuid.uuid4()
    
    await audit_service.registrar_evento(
        db, tenant_id=tenant_id, actor_id=actor_id,
        actor_email="test@test.com", accion="TEST_ACTION",
        entidad="Test", entidad_id="123"
    )
    
    # Verificar en DB
    result = await db.execute(select(AuditLog).filter(AuditLog.accion == "TEST_ACTION"))
    log = result.scalars().first()
    assert log is not None
    assert log.usuario_id == actor_id

@pytest.mark.asyncio
async def test_audit_log_no_editable(client: AsyncClient):
    # Intentar un PATCH a una ruta inexistente o bloqueada de auditoría
    # Como no definimos endpoints de edición para auditoría, debería dar 404 o 405
    response = await client.patch("/v1/auditoria/log/123", json={"accion": "HACKED"})
    assert response.status_code in [404, 405]

@pytest.mark.asyncio
async def test_audit_log_no_eliminable(client: AsyncClient):
    # Intentar un DELETE
    response = await client.delete("/v1/auditoria/log/123")
    assert response.status_code in [404, 405]

@pytest.mark.asyncio
async def test_audit_payload_antes_y_despues(db: AsyncSession):
    tenant_id = uuid.uuid4()
    await audit_service.registrar_evento(
        db, tenant_id=tenant_id, actor_id=uuid.uuid4(),
        actor_email="admin@test.com", accion="UPDATE_ALUMNO",
        payload_antes={"nombre": "Juan"},
        payload_despues={"nombre": "Juan Pablo"}
    )
    
    result = await db.execute(select(AuditLog).filter(AuditLog.accion == "UPDATE_ALUMNO"))
    log = result.scalars().first()
    assert log.payload_antes == {"nombre": "Juan"}
    assert log.payload_despues == {"nombre": "Juan Pablo"}
