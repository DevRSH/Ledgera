import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.folio import FolioCounter

async def generar_folio(db: AsyncSession, tenant_id: uuid.UUID, año: int, curso: str, tipo: str) -> str:
    """
    Genera un folio único correlativo para un tipo de documento específico.
    Formato: "2026-5B-PAG-0042"
    
    Usa SELECT FOR UPDATE para evitar condiciones de carrera.
    """
    async with db.begin_nested():
        # Buscar el contador actual con bloqueo de fila
        stmt = (
            select(FolioCounter)
            .filter(
                FolioCounter.tenant_id == tenant_id,
                FolioCounter.año == año,
                FolioCounter.curso == curso,
                FolioCounter.tipo == tipo
            )
            .with_for_update()
        )
        
        result = await db.execute(stmt)
        counter = result.scalars().first()
        
        if not counter:
            # Crear contador si no existe
            counter = FolioCounter(
                tenant_id=tenant_id,
                año=año,
                curso=curso,
                tipo=tipo,
                secuencia=1
            )
            db.add(counter)
            await db.flush()
        else:
            # Incrementar secuencia
            counter.secuencia += 1
            
        # Formatear el folio
        # Ejemplo: 2026-5B-PAG-0001
        folio = f"{año}-{curso}-{tipo}-{str(counter.secuencia).zfill(4)}"
        
        return folio
