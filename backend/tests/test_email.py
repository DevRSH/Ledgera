import pytest
from app.services.email_service import email_service

@pytest.mark.asyncio
async def test_render_template():
    template = "Hola {{nombre}}!"
    rendered = email_service._render_template(template, {"nombre": "Mundo"})
    assert rendered == "Hola Mundo!"

@pytest.mark.asyncio
async def test_enviar_comprobante_mock(db):
    import uuid
    test_tenant_id = uuid.uuid4()
    # Tests the mock path when API_KEY is missing
    msg_id = await email_service.enviar_comprobante_pago(
        db,
        tenant_id=test_tenant_id,

        apoderado_email="test@test.com",
        apoderado_nombre="Test Apoderado",
        pdf_bytes=b"fake-pdf",
        folio="2026-TEST-001",
        mes_año="Mayo 2026",
        monto=20000
    )
    assert msg_id == "mock-id"
