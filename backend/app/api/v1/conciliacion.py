import uuid
import csv
import io
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.usuario import Usuario
from app.models.conciliacion import ConciliacionBancaria, LineaBancaria
from app.schemas.conciliacion import (
    ConciliacionCreate, ConciliacionResponse, ConciliacionListResponse,
    LineaBancariaCreate, ConciliarLineaRequest
)
from app.services.conciliacion_service import conciliacion_service
from app.services import audit_service

router = APIRouter()

@router.post("", response_model=ConciliacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_conciliacion(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["TESORERO", "SUPER_ADMIN"])),
    obj_in: ConciliacionCreate
):
    """
    Crea un nuevo período de conciliación bancaria.
    """
    nueva = ConciliacionBancaria(
        tenant_id=current_user.tenant_id,
        año=obj_in.año,
        mes=obj_in.mes,
        banco=obj_in.banco,
        numero_cuenta=obj_in.numero_cuenta,
        saldo_inicial=obj_in.saldo_inicial,
        saldo_final=obj_in.saldo_final,
        estado="en_proceso"
    )
    db.add(nueva)
    await db.flush()
    
    await audit_service.registrar_evento(
        db, tenant_id=current_user.tenant_id, actor_id=current_user.id,
        actor_email=current_user.email, accion="CREATE_CONCILIACION",
        entidad="ConciliacionBancaria", entidad_id=str(nueva.id)
    )
    
    await db.commit()
    return nueva

@router.get("", response_model=ConciliacionListResponse)
async def listar_conciliaciones(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "TESORERO", "DIRECTIVA", "SUPER_ADMIN"])),
    año: Optional[int] = Query(None),
    mes: Optional[int] = Query(None),
    page: int = 1,
    size: int = 20
):
    stmt = select(ConciliacionBancaria).filter(ConciliacionBancaria.tenant_id == current_user.tenant_id)
    if año:
        stmt = stmt.filter(ConciliacionBancaria.año == año)
    if mes:
        stmt = stmt.filter(ConciliacionBancaria.mes == mes)
    
    # Pagination
    total_stmt = select(func.count()).select_from(stmt.subquery())
    total_res = await db.execute(total_stmt)
    total = total_res.scalar() or 0
    
    stmt = stmt.offset((page - 1) * size).limit(size)
    result = await db.execute(stmt)
    data = result.scalars().all()
    
    return {
        "data": data,
        "total": total,
        "page": page,
        "size": size
    }

@router.get("/{id}", response_model=ConciliacionResponse)
async def obtener_conciliacion(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "TESORERO", "DIRECTIVA", "SUPER_ADMIN"]))
):
    stmt = select(ConciliacionBancaria).filter(
        ConciliacionBancaria.id == id, 
        ConciliacionBancaria.tenant_id == current_user.tenant_id
    )
    result = await db.execute(stmt)
    conciliacion = result.scalars().first()
    if not conciliacion:
        raise HTTPException(status_code=404, detail="Conciliación no encontrada")
    return conciliacion

@router.post("/{id}/importar-lineas")
async def importar_lineas_csv(
    id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["TESORERO", "SUPER_ADMIN"]))
):
    """
    Importa líneas bancarias desde un CSV (formato: fecha;descripcion;monto).
    """
    conciliacion = await db.get(ConciliacionBancaria, id)
    if not conciliacion or conciliacion.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Conciliación no encontrada")

    content = await file.read()
    decoded = content.decode("utf-8")
    csv_reader = csv.reader(io.StringIO(decoded), delimiter=';')
    
    importadas = 0
    errores = []
    
    for i, row in enumerate(csv_reader, start=1):
        try:
            if len(row) < 3:
                raise ValueError("Fila incompleta")
            
            # Parsing básico (ajustar formatos de fecha según necesidad)
            nueva_linea = LineaBancaria(
                conciliacion_id=id,
                fecha=row[0], # El modelo espera date, SQLAlchemy hará la conversión si el formato es ISO
                descripcion=row[1],
                monto=int(row[2].replace(".", "")) # Limpieza básica de puntos si vienen en el monto
            )
            db.add(nueva_linea)
            importadas += 1
        except Exception as e:
            errores.append({"fila": i, "motivo": str(e)})

    await db.commit()
    return {"importadas": importadas, "errores": errores}

@router.post("/{id}/lineas/{linea_id}/conciliar")
async def conciliar_manualmente(
    id: uuid.UUID,
    linea_id: uuid.UUID,
    body: ConciliarLineaRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["TESORERO", "SUPER_ADMIN"]))
):
    linea = await db.get(LineaBancaria, linea_id)
    if not linea or linea.conciliacion_id != id:
        raise HTTPException(status_code=404, detail="Línea bancaria no encontrada")
    
    linea.movimiento_id = body.movimiento_id
    linea.conciliada = True
    linea.observacion = body.observacion
    
    await db.commit()
    return {"status": "ok"}

@router.post("/{id}/auto-conciliar")
async def auto_conciliar(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["TESORERO", "SUPER_ADMIN"]))
):
    res = await conciliacion_service.auto_conciliar(db, id)
    # Nota: El service actual hace commit, lo cual corregiremos luego, 
    # pero por ahora el router cumple su función.
    return res

@router.get("/{id}/diferencias", response_model=List[dict])
async def obtener_diferencias(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "TESORERO", "SUPER_ADMIN"]))
):
    stmt = select(LineaBancaria).filter(
        LineaBancaria.conciliacion_id == id,
        LineaBancaria.conciliada == False
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/{id}/cerrar")
async def cerrar_conciliacion(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["DIRECTIVA", "SUPER_ADMIN"]))
):
    conciliacion = await db.get(ConciliacionBancaria, id)
    if not conciliacion:
        raise HTTPException(status_code=404, detail="Conciliación no encontrada")
    
    # Verificar si hay diferencias
    stmt_diff = select(func.count()).select_from(LineaBancaria).filter(
        LineaBancaria.conciliacion_id == id,
        LineaBancaria.conciliada == False
    )
    res_diff = await db.execute(stmt_diff)
    tiene_diferencias = res_diff.scalar() > 0
    
    conciliacion.estado = "con_diferencias" if tiene_diferencias else "conciliada"
    conciliacion.conciliado_por = current_user.id
    conciliacion.conciliado_at = func.now()
    
    await audit_service.registrar_evento(
        db, tenant_id=current_user.tenant_id, actor_id=current_user.id,
        actor_email=current_user.email, accion="CLOSE_CONCILIACION",
        entidad="ConciliacionBancaria", entidad_id=str(id),
        payload_despues={"estado": conciliacion.estado}
    )
    
    await db.commit()
    return {"estado": conciliacion.estado}
