import uuid
from datetime import date, datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, ConfigDict, Field

class ValeBase(BaseModel):
    tipo: Literal["ingreso", "egreso"]
    concepto: str = Field(..., max_length=500)
    monto: int = Field(..., gt=0)
    fecha: date
    recibe_nombre: str = Field(..., max_length=200)
    observaciones: Optional[str] = None
    movimiento_id: Optional[uuid.UUID] = None

class ValeCreate(ValeBase):
    pass

class ValeResponse(ValeBase):
    id: uuid.UUID
    folio: str
    entrega_nombre: str
    pdf_url: Optional[str] = None
    anulado: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ValeListResponse(BaseModel):
    data: List[ValeResponse]
    total: int
    page: int
    size: int
