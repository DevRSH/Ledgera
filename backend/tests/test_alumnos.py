import pytest
from app.core.utils import validar_rut_chileno

@pytest.mark.asyncio
async def test_validate_rut():
    assert validar_rut_chileno("12.345.678-5") == "12345678-5"
    assert validar_rut_chileno("12345678-5") == "12345678-5"
    assert validar_rut_chileno("11.111.111-1") == "11111111-1"
    
    with pytest.raises(ValueError):
        validar_rut_chileno("11.111.111-2") # Invalid checksum
        
    with pytest.raises(ValueError):
        validar_rut_chileno("K-1") # Too short

@pytest.mark.asyncio
async def test_api_list_alumnos_empty(client):
    # We need a user and a token to test protected routes
    # For now, let's just test that it requires auth
    response = await client.get("/v1/alumnos/")
    assert response.status_code == 401
