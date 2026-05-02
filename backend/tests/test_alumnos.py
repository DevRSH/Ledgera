import pytest
from app.core.utils import validate_rut, format_rut

@pytest.mark.asyncio
async def test_validate_rut():
    assert validate_rut("12.345.678-5") is True
    assert validate_rut("12345678-5") is True
    assert validate_rut("11.111.111-1") is True
    assert validate_rut("11.111.111-2") is False # Invalid checksum
    assert validate_rut("K-1") is False # Too short

@pytest.mark.asyncio
async def test_format_rut():
    assert format_rut("123456785") == "12345678-5"
    assert format_rut("12.345.678-5") == "12345678-5"

@pytest.mark.asyncio
async def test_api_list_alumnos_empty(client):
    # We need a user and a token to test protected routes
    # For now, let's just test that it requires auth
    response = await client.get("/v1/alumnos/")
    assert response.status_code == 401
