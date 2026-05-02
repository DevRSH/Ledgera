import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

class ComprobanteResponse(BaseModel):
    id: uuid.UUID
    folio: str
    alumno_nombre: Optional[str] = None # Se poblará desde la relación
    mes: int
    año: int
    monto: int
    fecha_pago: date
    recibido_por_nombre: str
    pdf_url: Optional[str] = None
    qr_verification_url: str
    anulado: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class AnularComprobanteRequest(BaseModel):
    motivo: str = Field(..., min_length=10)

class VerificacionPublicaResponse(BaseModel):
    valido: bool
    folio: Optional[str] = None
    concepto: Optional[str] = None # Ej: Pago Cuota 05/2026
    monto: Optional[int] = None
    fecha_pago: Optional[date] = None
    motivo: Optional[str] = None # En caso de que sea inválido o esté anulado
    
    # IMPORTANTE: No incluir PII (Personal Identifiable Information) como el nombre del alumno
    
    model_config = ConfigDict(from_attributes=True)

class ComprobanteListResponse(BaseModel):
    data: List[ComprobanteResponse]
    total: int
    page: int
    size: int
