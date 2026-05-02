import pytest
import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.folio_service import generar_folio
from app.models.folio import FolioCounter

@pytest.mark.asyncio
async def test_folio_formato_correcto(db: AsyncSession):
    tenant_id = uuid.uuid4()
    folio = await generar_folio(db, tenant_id, 2026, "5B", "PAG")
    # Formato: 2026-5B-PAG-0001
    assert folio == "2026-5B-PAG-0001"

@pytest.mark.asyncio
async def test_folio_correlativo_secuencial(db: AsyncSession):
    tenant_id = uuid.uuid4()
    f1 = await generar_folio(db, tenant_id, 2026, "5B", "PAG")
    f2 = await generar_folio(db, tenant_id, 2026, "5B", "PAG")
    assert f1 == "2026-5B-PAG-0001"
    assert f2 == "2026-5B-PAG-0002"

@pytest.mark.asyncio
async def test_folio_tipos_secuencia_independiente(db: AsyncSession):
    tenant_id = uuid.uuid4()
    f_pag = await generar_folio(db, tenant_id, 2026, "5B", "PAG")
    f_val = await generar_folio(db, tenant_id, 2026, "5B", "VAL-E")
    assert f_pag == "2026-5B-PAG-0001"
    assert f_val == "2026-5B-VAL-E-0001"

@pytest.mark.asyncio
async def test_folio_cursos_independientes(db: AsyncSession):
    tenant_id = uuid.uuid4()
    f_5b = await generar_folio(db, tenant_id, 2026, "5B", "PAG")
    f_3a = await generar_folio(db, tenant_id, 2026, "3A", "PAG")
    assert f_5b == "2026-5B-PAG-0001"
    assert f_3a == "2026-3A-PAG-0001"

@pytest.mark.asyncio
async def test_folio_años_independientes(db: AsyncSession):
    tenant_id = uuid.uuid4()
    f_2025 = await generar_folio(db, tenant_id, 2025, "5B", "PAG")
    f_2026 = await generar_folio(db, tenant_id, 2026, "5B", "PAG")
    assert f_2025 == "2025-5B-PAG-0001"
    assert f_2026 == "2026-5B-PAG-0001"

@pytest.mark.asyncio
async def test_100_folios_concurrentes_sin_duplicados(db: AsyncSession):
    tenant_id = uuid.uuid4()
    año = 2026
    curso = "5B"
    tipo = "PAG"
    
    # Creamos 100 corrutinas que intentan generar un folio al mismo tiempo
    # En un entorno real, SELECT FOR UPDATE bloquearía las filas.
    # En SQLite aiosqlite, el bloqueo es a nivel de base de datos o manejado por el driver.
    
    tasks = []
    for _ in range(100):
        tasks.append(generar_folio(db, tenant_id, año, curso, tipo))
    
    folios = await asyncio.gather(*tasks)
    
    # Verificamos que tengamos 100 folios únicos
    assert len(folios) == 100
    assert len(set(folios)) == 100
    
    # El último debería ser el 0100
    assert "2026-5B-PAG-0100" in folios
