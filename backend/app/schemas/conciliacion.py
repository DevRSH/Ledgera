import uuid
from datetime import date, datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field

class LineaBancariaCreate(BaseModel):
    fecha: date
    descripcion: str = Field(..., max_length=500)
    monto: int

class ConciliacionCreate(BaseModel):
    año: int = Field(..., ge=2020, le=2100)
    mes: int = Field(..., ge=1, le=12)
    banco: Optional[str] = None
    numero_cuenta: Optional[str] = None
    saldo_inicial: int
    saldo_final: int

class ConciliarLineaRequest(BaseModel):
    movimiento_id: uuid.UUID
    observacion: Optional[str] = None

class ConciliacionResponse(BaseModel):
    id: uuid.UUID
    año: int
    mes: int
    estado: str # 'en_proceso', 'conciliada', 'con_diferencias'
    diferencia: int = 0
    total_lineas: int = 0
    lineas_conciliadas: int = 0
    lineas_pendientes: int = 0
    
    model_config = ConfigDict(from_attributes=True)

class ConciliacionListResponse(BaseModel):
    data: List[ConciliacionResponse]
    total: int
    page: int
    size: int
