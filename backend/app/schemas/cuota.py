import uuid
from datetime import date, datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field

class ConfigCuotaCreate(BaseModel):
    año: int = Field(..., ge=2020, le=2100)
    mes: int = Field(..., ge=1, le=12)
    monto: int = Field(..., ge=0)
    descripcion: Optional[str] = None
    fecha_vencimiento: Optional[date] = None

class RegistrarPagoRequest(BaseModel):
    alumno_id: uuid.UUID
    mes: int = Field(..., ge=1, le=12)
    año: int = Field(..., ge=2020, le=2100)
    monto: int = Field(..., gt=0)
    forma_pago: str # 'efectivo', 'transferencia', etc.

class EstadoDeudaResponse(BaseModel):
    alumno_id: uuid.UUID
    alumno_nombre: str
    meses_adeudados: int
    monto_adeudado: int
    estado: str # 'al_dia', 'debe_1_2', 'debe_3_mas', 'condonado_total'
    ultimo_pago: Optional[date] = None
    
    model_config = ConfigDict(from_attributes=True)

class NominaDeudoresResponse(BaseModel):
    data: List[EstadoDeudaResponse]
    total_deuda: int

class CondonacionCreate(BaseModel):
    alumno_id: uuid.UUID
    año: int = Field(..., ge=2020, le=2100)
    mes: Optional[int] = Field(None, ge=1, le=12, description="Si es nulo, aplica a todo el año")
    motivo: str = Field(..., min_length=20)

# Para listados estándar si se requirieran
class ConfigCuotaResponse(ConfigCuotaCreate):
    id: uuid.UUID
    tenant_id: uuid.UUID
    model_config = ConfigDict(from_attributes=True)

class ConfigCuotaListResponse(BaseModel):
    data: List[ConfigCuotaResponse]
    total: int
    page: int
    size: int

# Alias para compatibilidad con los services
EstadoDeuda = EstadoDeudaResponse
