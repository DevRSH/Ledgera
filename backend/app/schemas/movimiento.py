import uuid
from datetime import date, datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field

class MovimientoBase(BaseModel):
    tipo: Literal["ingreso", "egreso"]
    monto: int = Field(gt=0, description="Monto en CLP, debe ser mayor a 0")
    fecha: date
    descripcion: str = Field(max_length=500)
    categoria_id: Optional[uuid.UUID] = None
    forma_pago: Literal["efectivo", "transferencia", "cheque", "otro"]
    referencia_bancaria: Optional[str] = None

class MovimientoCreate(MovimientoBase):
    pass

class MovimientoUpdate(BaseModel):
    descripcion: Optional[str] = Field(None, max_length=500)
    categoria_id: Optional[uuid.UUID] = None
    referencia_bancaria: Optional[str] = None

class MovimientoResponse(MovimientoBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    registrado_por: uuid.UUID
    anulado: bool
    anulado_por: Optional[uuid.UUID] = None
    anulado_at: Optional[datetime] = None
    motivo_anulacion: Optional[str] = None
    conciliado: bool
    created_at: datetime
    
    # Campos adicionales solicitados
    nombre_categoria: Optional[str] = None
    nombre_registrado_por: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class MovimientoListResponse(BaseModel):
    data: List[MovimientoResponse]
    total: int
    page: int
    size: int

class AnularMovimientoRequest(BaseModel):
    motivo: str = Field(..., min_length=10, description="El motivo de anulación es obligatorio")
