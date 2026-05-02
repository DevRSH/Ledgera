import csv
import io
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.core.database import get_db
from app.models.usuario import Usuario
from app.models.alumno import Alumno, Apoderado
from app.core.dependencies import get_current_user
from app.core.utils import validate_rut, format_rut
from pydantic import BaseModel, EmailStr

router = APIRouter()

# Schemas
class ApoderadoBase(BaseModel):
    tipo: str
    rut: Optional[str] = None
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class AlumnoCreate(BaseModel):
    rut: str
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    fecha_nacimiento: Optional[str] = None # date in ISO format
    observaciones: Optional[str] = None
    apoderados: List[ApoderadoBase] = []

class AlumnoResponse(BaseModel):
    id: Any
    rut: str
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    activo: bool

@router.get("/", response_model=List[AlumnoResponse])
async def list_alumnos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    List all students for the current tenant.
    """
    result = await db.execute(
        select(Alumno)
        .filter(Alumno.tenant_id == current_user.tenant_id)
        .filter(Alumno.deleted_at == None)
    )
    return result.scalars().all()

@router.post("/", response_model=AlumnoResponse)
async def create_alumno(
    alumno_in: AlumnoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Create a new student with optional apoderados.
    """
    if not validate_rut(alumno_in.rut):
        raise HTTPException(status_code=400, detail="RUT inválido")
    
    # Check if RUT already exists for this tenant
    result = await db.execute(
        select(Alumno).filter(Alumno.tenant_id == current_user.tenant_id, Alumno.rut == alumno_in.rut)
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="El RUT ya existe en este curso")
    
    new_alumno = Alumno(
        tenant_id=current_user.tenant_id,
        rut=format_rut(alumno_in.rut),
        nombre=alumno_in.nombre,
        apellido_paterno=alumno_in.apellido_paterno,
        apellido_materno=alumno_in.apellido_materno,
        observaciones=alumno_in.observaciones
    )
    db.add(new_alumno)
    await db.flush() # Get ID
    
    for apo_in in alumno_in.apoderados:
        new_apo = Apoderado(
            alumno_id=new_alumno.id,
            **apo_in.model_dump()
        )
        db.add(new_apo)
        
    await db.commit()
    await db.refresh(new_alumno)
    return new_alumno

@router.post("/importar-csv")
async def importar_alumnos(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    """
    Mass import students from CSV.
    """
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    results = {"creados": 0, "errores": []}
    
    for row in reader:
        try:
            # Basic mapping (simplified for this turn)
            rut = row.get("rut")
            if not rut or not validate_rut(rut):
                results["errores"].append({"fila": row, "motivo": "RUT inválido"})
                continue
                
            new_alumno = Alumno(
                tenant_id=current_user.tenant_id,
                rut=format_rut(rut),
                nombre=row.get("nombre", ""),
                apellido_paterno=row.get("apellido_paterno", ""),
                apellido_materno=row.get("apellido_materno")
            )
            db.add(new_alumno)
            results["creados"] += 1
        except Exception as e:
            results["errores"].append({"fila": row, "motivo": str(e)})
            
    await db.commit()
    return results
