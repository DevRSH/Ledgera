import csv
import io
import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import joinedload

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.usuario import Usuario
from app.models.alumno import Alumno, Apoderado
from app.core.utils import validar_rut_chileno
from app.schemas.alumno import AlumnoCreate, AlumnoUpdate, AlumnoResponse, AlumnoListResponse
from app.services import audit_service

router = APIRouter()

@router.get("/", response_model=AlumnoListResponse)
async def list_alumnos(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "TESORERO", "DIRECTIVA", "SUPER_ADMIN"])),
    page: int = 1,
    size: int = 50
) -> Any:
    stmt = select(Alumno).filter(
        Alumno.tenant_id == current_user.tenant_id, 
        Alumno.activo == True
    ).options(joinedload(Alumno.apoderados)).offset((page - 1) * size).limit(size)
    
    result = await db.execute(stmt)
    alumnos = result.unique().scalars().all()
    
    total_result = await db.execute(
        select(func.count(Alumno.id)).filter(
            Alumno.tenant_id == current_user.tenant_id, 
            Alumno.activo == True
        )
    )
    total = total_result.scalar() or 0
    
    return {
        "data": alumnos,
        "total": total,
        "page": page,
        "size": size
    }

@router.post("/", response_model=AlumnoResponse, status_code=status.HTTP_201_CREATED)
async def create_alumno(
    alumno_in: AlumnoCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["TESORERO", "SUPER_ADMIN"]))
) -> Any:
    result = await db.execute(
        select(Alumno).filter(Alumno.tenant_id == current_user.tenant_id, Alumno.rut == alumno_in.rut)
    )
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="El RUT ya existe en el sistema")
    
    new_alumno = Alumno(
        tenant_id=current_user.tenant_id,
        rut=alumno_in.rut,
        nombre=alumno_in.nombre,
        apellido_paterno=alumno_in.apellido_paterno,
        apellido_materno=alumno_in.apellido_materno,
        fecha_nacimiento=alumno_in.fecha_nacimiento,
        observaciones=alumno_in.observaciones
    )
    db.add(new_alumno)
    await db.flush()
    
    await audit_service.registrar_evento(
        db, tenant_id=current_user.tenant_id, actor_id=current_user.id,
        actor_email=current_user.email, accion=audit_service.CREATE_ALUMNO,
        entidad="Alumno", entidad_id=str(new_alumno.id),
        payload_despues=alumno_in.model_dump(mode='json')
    )
    
    await db.commit()
    # Reload with relationships
    result = await db.execute(
        select(Alumno).filter(Alumno.id == new_alumno.id).options(joinedload(Alumno.apoderados))
    )
    return result.unique().scalars().first()

@router.get("/{id}", response_model=AlumnoResponse)
async def get_alumno(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "TESORERO", "DIRECTIVA", "SUPER_ADMIN"]))
) -> Any:
    result = await db.execute(
        select(Alumno).filter(Alumno.id == id).options(joinedload(Alumno.apoderados))
    )
    alumno = result.unique().scalars().first()
    if not alumno or alumno.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    return alumno

@router.patch("/{id}", response_model=AlumnoResponse)
async def update_alumno(
    id: uuid.UUID,
    alumno_in: AlumnoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["TESORERO", "SUPER_ADMIN"]))
) -> Any:
    result = await db.execute(
        select(Alumno).filter(Alumno.id == id).options(joinedload(Alumno.apoderados))
    )
    alumno = result.unique().scalars().first()
    if not alumno or alumno.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    payload_antes = {"nombre": alumno.nombre, "activo": alumno.activo}
    update_data = alumno_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(alumno, key, value)
    
    await audit_service.registrar_evento(
        db, tenant_id=current_user.tenant_id, actor_id=current_user.id,
        actor_email=current_user.email, accion=audit_service.UPDATE_ALUMNO,
        entidad="Alumno", entidad_id=str(id),
        payload_antes=payload_antes, payload_despues=update_data
    )
    
    await db.commit()
    # Refresh to ensure relationships are loaded correctly
    result = await db.execute(
        select(Alumno).filter(Alumno.id == id).options(joinedload(Alumno.apoderados))
    )
    return result.unique().scalars().first()

@router.post("/importar-csv")
async def importar_alumnos(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["TESORERO", "SUPER_ADMIN"]))
) -> Any:
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))
    
    importados = 0
    errores = []
    
    for i, row in enumerate(reader, start=1):
        try:
            rut = validar_rut_chileno(row.get("rut", ""))
            new_alumno = Alumno(
                tenant_id=current_user.tenant_id,
                rut=rut,
                nombre=row.get("nombre", ""),
                apellido_paterno=row.get("apellido_paterno", ""),
                apellido_materno=row.get("apellido_materno")
            )
            db.add(new_alumno)
            importados += 1
        except Exception as e:
            errores.append({"fila": i, "motivo": str(e)})
            
    await audit_service.registrar_evento(
        db, tenant_id=current_user.tenant_id, actor_id=current_user.id,
        actor_email=current_user.email, accion="IMPORT_ALUMNOS",
        payload_despues={"importados": importados, "errores": len(errores)}
    )
    
    await db.commit()
    return {"importados": importados, "errores": errores}
