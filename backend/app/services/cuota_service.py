import uuid
from datetime import datetime
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, not_
from fastapi import HTTPException, status

from app.models.cuota import ConfiguracionCuota, PagoCuota, Condonacion
from app.models.alumno import Alumno
from app.models.usuario import Usuario
from app.schemas.cuota import EstadoDeuda
from app.services import folio_service, audit_service, movimiento_service

async def calcular_estado_deuda(db: AsyncSession, tenant_id: uuid.UUID, alumno_id: uuid.UUID, año: int) -> EstadoDeuda:
    """
    Calcula el estado de deuda detallado de un alumno para un año específico.
    """
    # 1. Obtener meses configurados para el año
    stmt_config = select(ConfiguracionCuota).filter(
        ConfiguracionCuota.tenant_id == tenant_id,
        ConfiguracionCuota.año == año
    ).order_by(ConfiguracionCuota.mes)
    res_config = await db.execute(stmt_config)
    configuraciones = res_config.scalars().all()
    
    if not configuraciones:
        return EstadoDeuda(
            meses_configurados=0, meses_pagados=0, meses_condonados=0,
            meses_adeudados=0, monto_adeudado=0, estado="al_dia"
        )

    # 2. Obtener meses pagados
    stmt_pagos = select(PagoCuota.mes).filter(
        PagoCuota.tenant_id == tenant_id,
        PagoCuota.alumno_id == alumno_id,
        PagoCuota.año == año
    )
    res_pagos = await db.execute(stmt_pagos)
    meses_pagados_list = res_pagos.scalars().all()

    # 3. Obtener meses condonados
    stmt_condon = select(Condonacion.mes).filter(
        Condonacion.tenant_id == tenant_id,
        Condonacion.alumno_id == alumno_id,
        Condonacion.año == año
    )
    res_condon = await db.execute(stmt_condon)
    meses_condonados_raw = res_condon.scalars().all()
    
    # Manejar condonación de año completo (mes is NULL)
    condonacion_total = any(m is None for m in meses_condonados_raw)
    meses_condonados_set = set(m for m in meses_condonados_raw if m is not None)

    # 4. Calcular deudas
    meses_adeudados = 0
    monto_adeudado = 0
    
    if not condonacion_total:
        for conf in configuraciones:
            if conf.mes not in meses_pagados_list and conf.mes not in meses_condonados_set:
                meses_adeudados += 1
                monto_adeudado += conf.monto

    # 5. Determinar estado
    estado = "al_dia"
    if condonacion_total:
        estado = "condonado_total"
    elif meses_adeudados >= 3:
        estado = "debe_3_mas"
    elif meses_adeudados > 0:
        estado = "debe_1_2"

    return EstadoDeuda(
        meses_configurados=len(configuraciones),
        meses_pagados=len(meses_pagados_list),
        meses_condonados=len(configuraciones) if condonacion_total else len(meses_condonados_set),
        meses_adeudados=0 if condonacion_total else meses_adeudados,
        monto_adeudado=0 if condonacion_total else monto_adeudado,
        estado=estado
    )

async def obtener_deudores(db: AsyncSession, tenant_id: uuid.UUID, año: int) -> List[Tuple[Alumno, EstadoDeuda]]:
    """
    Obtiene la lista de alumnos con deuda pendiente.
    """
    stmt_alumnos = select(Alumno).filter(Alumno.tenant_id == tenant_id, Alumno.activo == True)
    res_alumnos = await db.execute(stmt_alumnos)
    alumnos = res_alumnos.scalars().all()
    
    deudores = []
    for alumno in alumnos:
        estado = await calcular_estado_deuda(db, tenant_id, alumno.id, año)
        if estado.meses_adeudados > 0:
            deudores.append((alumno, estado))
            
    # Ordenar por monto adeudado DESC
    deudores.sort(key=lambda x: x[1].monto_adeudado, reverse=True)
    return deudores

async def registrar_pago(
    db: AsyncSession, 
    tenant_id: uuid.UUID, 
    actor: Usuario, 
    alumno_id: uuid.UUID, 
    mes: int, 
    año: int, 
    monto: int,
    forma_pago: str
) -> Tuple[PagoCuota, str]:
    """
    Registra el pago de una cuota, crea el movimiento contable y genera el folio.
    """
    # 1. Verificar si ya existe el pago (Unique Constraint prevention)
    stmt_check = select(PagoCuota).filter(
        PagoCuota.tenant_id == tenant_id,
        PagoCuota.alumno_id == alumno_id,
        PagoCuota.año == año,
        PagoCuota.mes == mes
    )
    result_check = await db.execute(stmt_check)
    if result_check.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un pago registrado para el mes {mes}/{año}."
        )

    # 2. Obtener datos del alumno para el folio (curso)
    alumno = await db.get(Alumno, alumno_id)
    if not alumno:
        raise HTTPException(status_code=404, detail="Alumno no encontrado.")
    
    # Nota: Aquí asumo que el curso se obtiene de la configuración o del alumno. 
    # Para el folio usaremos un valor genérico o el que tenga el contador si existe.
    # En este sistema, los folios de pago suelen ser por curso.
    curso_folio = "GEN" # Valor por defecto si no se especifica curso en el alumno
    # Si el alumno tuviera campo 'curso', lo usaríamos aquí.

    # 3. Generar Folio
    folio = await folio_service.generar_folio(db, tenant_id, año, curso_folio, "PAG")

    # 4. Crear Movimiento de Ingreso
    movimiento_data = {
        "tipo": "ingreso",
        "monto": monto,
        "descripcion": f"Pago Cuota Mes {mes}/{año} - Alumno: {alumno.nombre} {alumno.apellido_paterno}",
        "forma_pago": forma_pago,
        "categoria_id": None # Podría buscarse una categoría "Cuotas" si existiera
    }
    movimiento = await movimiento_service.crear_movimiento(db, tenant_id, actor, movimiento_data)

    # 5. Registrar el Pago de Cuota
    nuevo_pago = PagoCuota(
        tenant_id=tenant_id,
        alumno_id=alumno_id,
        año=año,
        mes=mes,
        monto_pagado=monto,
        fecha_pago=datetime.utcnow().date(),
        movimiento_id=movimiento.id,
        registrado_por=actor.id,
        observaciones=f"Folio: {folio}"
    )
    
    db.add(nuevo_pago)
    await db.flush()

    # 6. Auditoría Extra
    await audit_service.registrar_evento(
        db,
        tenant_id=tenant_id,
        actor_id=actor.id,
        actor_email=actor.email,
        accion=audit_service.REGISTRAR_PAGO,
        entidad="PagoCuota",
        entidad_id=str(nuevo_pago.id),
        payload_despues={"mes": mes, "año": año, "folio": folio}
    )

    return nuevo_pago, folio
