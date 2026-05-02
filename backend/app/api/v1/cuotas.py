import uuid
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.models.usuario import Usuario
from app.models.cuota import ConfiguracionCuota, PagoCuota
from app.schemas.cuota import (
    ConfigCuotaCreate, RegistrarPagoRequest, EstadoDeudaResponse, 
    NominaDeudoresResponse, CondonacionCreate
)
from app.services import cuota_service, audit_service

router = APIRouter()

@router.get("/config", response_model=List[Any])
async def get_config(
    año: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "TESORERO", "SUPER_ADMIN"]))
) -> Any:
    stmt = select(ConfiguracionCuota).filter(
        ConfiguracionCuota.tenant_id == current_user.tenant_id, 
        ConfiguracionCuota.año == año
    )
    result = await db.execute(stmt)
    return result.scalars().all()

@router.post("/config", status_code=status.HTTP_201_CREATED)
async def set_config(
    configs: List[ConfigCuotaCreate],
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["TESORERO", "SUPER_ADMIN"]))
) -> Any:
    """
    Configura los montos de las cuotas para un año.
    """
    for cfg_in in configs:
        # Verificar si ya existe para ese mes/año para actualizar o crear
        stmt = select(ConfiguracionCuota).filter(
            ConfiguracionCuota.tenant_id == current_user.tenant_id,
            ConfiguracionCuota.año == cfg_in.año,
            ConfiguracionCuota.mes == cfg_in.mes
        )
        res = await db.execute(stmt)
        existing = res.scalars().first()
        
        if existing:
            existing.monto = cfg_in.monto
            existing.descripcion = cfg_in.descripcion
            existing.fecha_vencimiento = cfg_in.fecha_vencimiento
        else:
            new_cfg = ConfiguracionCuota(
                tenant_id=current_user.tenant_id,
                **cfg_in.model_dump()
            )
            db.add(new_cfg)
            
    await audit_service.registrar_evento(
        db, tenant_id=current_user.tenant_id, actor_id=current_user.id,
        actor_email=current_user.email, accion="UPDATE_CUOTA_CONFIG",
        payload_despues={"año": configs[0].año if configs else None, "count": len(configs)}
    )
    
    await db.commit()
    return {"status": "ok"}

@router.post("/pago", status_code=status.HTTP_201_CREATED)
async def registrar_pago(
    pago_in: RegistrarPagoRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["TESORERO", "SUPER_ADMIN"]))
) -> Any:
    """
    Registra un pago de cuota usando el cuota_service.
    Retorna el pago y el folio generado.
    """
    pago, folio = await cuota_service.registrar_pago(
        db, 
        tenant_id=current_user.tenant_id,
        actor=current_user,
        alumno_id=pago_in.alumno_id,
        mes=pago_in.mes,
        año=pago_in.año,
        monto=pago_in.monto,
        forma_pago=pago_in.forma_pago
    )
    
    await db.commit()
    return {"pago_id": str(pago.id), "folio": folio}

@router.get("/estado/{alumno_id}", response_model=EstadoDeudaResponse)
async def get_estado_deuda(
    alumno_id: uuid.UUID,
    año: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "TESORERO", "DIRECTIVA", "SUPER_ADMIN"]))
) -> Any:
    """
    Calcula el estado de deuda usando el motor de cuota_service.
    """
    from app.models.alumno import Alumno
    alumno = await db.get(Alumno, alumno_id)
    if not alumno or alumno.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
        
    estado = await cuota_service.calcular_estado_deuda(db, current_user.tenant_id, alumno_id, año)
    
    # Enriquecer con datos del alumno para el response
    return {
        **estado.model_dump(),
        "alumno_id": alumno_id,
        "alumno_nombre": f"{alumno.nombre} {alumno.apellido_paterno}"
    }

@router.get("/deudores", response_model=NominaDeudoresResponse)
async def list_deudores(
    año: int,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["AUDITOR", "TESORERO", "DIRECTIVA", "SUPER_ADMIN"]))
) -> Any:
    """
    Obtiene la nómina de deudores ordenada por monto.
    """
    deudores_raw = await cuota_service.obtener_deudores(db, current_user.tenant_id, año)
    
    data = []
    total_deuda = 0
    for alumno, estado in deudores_raw:
        data.append({
            **estado.model_dump(),
            "alumno_id": alumno.id,
            "alumno_nombre": f"{alumno.nombre} {alumno.apellido_paterno}"
        })
        total_deuda += estado.monto_adeudado
        
    return {"data": data, "total_deuda": total_deuda}

@router.post("/condonacion", status_code=status.HTTP_201_CREATED)
async def crear_condonacion(
    cond_in: CondonacionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_role(["DIRECTIVA", "SUPER_ADMIN"]))
) -> Any:
    """
    Registra una condonación de deuda (requiere rol DIRECTIVA).
    """
    from app.models.cuota import Condonacion
    nueva = Condonacion(
        tenant_id=current_user.tenant_id,
        alumno_id=cond_in.alumno_id,
        año=cond_in.año,
        mes=cond_in.mes,
        motivo=cond_in.motivo,
        autorizado_por=current_user.id
    )
    db.add(nueva)
    await db.flush()
    
    await audit_service.registrar_evento(
        db, tenant_id=current_user.tenant_id, actor_id=current_user.id,
        actor_email=current_user.email, accion="CREATE_CONDONACION",
        entidad="Condonacion", entidad_id=str(nueva.id),
        payload_despues=cond_in.model_dump(mode='json')
    )
    
    await db.commit()
    return {"status": "ok", "id": str(nueva.id)}
