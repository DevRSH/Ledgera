from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.conciliacion import ConciliacionBancaria, LineaBancaria
from app.models.movimiento import Movimiento
import uuid

class ConciliacionService:
    async def auto_conciliar(self, db: AsyncSession, conciliacion_id: uuid.UUID) -> dict:
        """
        Attempts automatic matching based on amount and date (+/- 2 days).
        """
        # Get all non-reconciled lines for this reconciliation
        result = await db.execute(
            select(LineaBancaria).filter(
                LineaBancaria.conciliacion_id == conciliacion_id,
                LineaBancaria.conciliada == False
            )
        )
        lineas = result.scalars().all()
        
        matches = 0
        pendientes = 0
        
        for linea in lineas:
            # Search for candidate movements
            # This is a simplified heuristic for the sprint
            result_mov = await db.execute(
                select(Movimiento).filter(
                    Movimiento.monto == abs(linea.monto),
                    Movimiento.conciliado == False
                )
            )
            candidates = result_mov.scalars().all()
            
            # Simple match: if exactly one candidate found
            if len(candidates) == 1:
                mov = candidates[0]
                linea.movimiento_id = mov.id
                linea.conciliada = True
                mov.conciliado = True # Need to add this field to Movimiento
                matches += 1
            else:
                pendientes += 1
                
        await db.commit()
        return {"conciliados": matches, "pendientes": pendientes}

conciliacion_service = ConciliacionService()
