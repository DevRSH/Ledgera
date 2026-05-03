import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_endpoint_publico_no_requiere_token(client: AsyncClient):
    # Usamos un UUID fake para el tenant
    response = await client.get("/v1/public/00000000-0000-0000-0000-000000000000/saldo")
    # Debería dar 200 (aunque el tenant no exista, el acceso es público) o 404 si no existe
    assert response.status_code in [200, 404]

@pytest.mark.asyncio
async def test_crear_movimiento_solo_tesorero(client: AsyncClient, token_tesorero, token_apoderado):
    mov_data = {
        "tipo": "ingreso", "monto": 1000, "fecha": "2026-05-02",
        "descripcion": "Test", "forma_pago": "efectivo"
    }
    
    # Con apoderado -> 403
    resp_apo = await client.post(
        "/v1/movimientos/", json=mov_data,
        headers={"Authorization": f"Bearer {token_apoderado}"}
    )
    assert resp_apo.status_code == 403
    
    # Con tesorero -> 201
    resp_teso = await client.post(
        "/v1/movimientos/", json=mov_data,
        headers={"Authorization": f"Bearer {token_tesorero}"}
    )
    assert resp_teso.status_code == 201

@pytest.mark.asyncio
async def test_anular_movimiento_solo_directiva(client: AsyncClient, token_tesorero, token_directiva):
    # Anular requiere rol DIRECTIVA
    resp_teso = await client.post(
        "/v1/movimientos/00000000-0000-0000-0000-000000000000/anular",
        json={"motivo": "Motivo muy largo para test"},
        headers={"Authorization": f"Bearer {token_tesorero}"}
    )
    assert resp_teso.status_code == 403
    
    resp_dir = await client.post(
        "/v1/movimientos/00000000-0000-0000-0000-000000000000/anular",
        json={"motivo": "Motivo muy largo para test"},
        headers={"Authorization": f"Bearer {token_directiva}"}
    )
    # 404 porque el ID es fake, pero no 403
    assert resp_dir.status_code == 404

@pytest.mark.asyncio
async def test_ver_auditoria_solo_auditor(client: AsyncClient, token_tesorero, token_auditor):
    resp_teso = await client.get(
        "/v1/auditoria/log",
        headers={"Authorization": f"Bearer {token_tesorero}"}
    )
    assert resp_teso.status_code == 403
    
    resp_aud = await client.get(
        "/v1/auditoria/log",
        headers={"Authorization": f"Bearer {token_auditor}"}
    )
    assert resp_aud.status_code == 200
