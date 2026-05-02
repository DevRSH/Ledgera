from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.usuario import Usuario
from app.models.reporte import ReporteJob
from app.core.dependencies import get_current_user
from app.services.reporte_service import reporte_service
from pydantic import BaseModel
from fastapi.responses import Response

router = APIRouter()

class JobResponse(BaseModel):
    id: Any
    tipo: str
    estado: str

@router.post("/nomina-deudores/export", response_class=Response)
async def export_nomina_deudores(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    # Logic to fetch deudores
    # Simplified mock for the sprint
    datos = [
        {"alumno": "Juan Perez", "deuda": 50000, "meses": "Marzo, Abril"},
        {"alumno": "Maria Gomez", "deuda": 25000, "meses": "Abril"}
    ]
    columnas = [
        {"header": "Alumno", "key": "alumno"},
        {"header": "Deuda Total", "key": "deuda"},
        {"header": "Meses Pendientes", "key": "meses"}
    ]
    
    xlsx_bytes = await reporte_service.exportar_xlsx(datos, columnas, "Nomina Deudores")
    
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=nomina_deudores.xlsx"}
    )

@router.get("/jobs", response_model=List[JobResponse])
async def list_jobs(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    result = await db.execute(
        select(ReporteJob).filter(ReporteJob.tenant_id == current_user.tenant_id)
    )
    return result.scalars().all()
