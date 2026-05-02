import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict

class ReporteJobCreate(BaseModel):
    tipo: str # 'flujo_caja', 'nomina_deudores', 'balance_anual', etc.
    parametros: Optional[Dict[str, Any]] = None

class ReporteJobResponse(BaseModel):
    id: uuid.UUID
    tipo: str
    estado: str # 'pendiente', 'procesando', 'completado', 'error'
    created_at: datetime
    completado_at: Optional[datetime] = None
    resultado_url: Optional[str] = None
    error_detalle: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ReporteJobListResponse(BaseModel):
    data: List[ReporteJobResponse]
    total: int
    page: int
    size: int
