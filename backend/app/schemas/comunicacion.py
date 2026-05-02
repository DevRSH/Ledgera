import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, EmailStr

class EnviarEstadoCuentaRequest(BaseModel):
    alumno_id: uuid.UUID

class EnvioMasivoResponse(BaseModel):
    total: int
    encolados: int
    sin_email: int

class EmailEnviadoResponse(BaseModel):
    id: uuid.UUID
    alumno_nombre: Optional[str] = None
    destinatario_email: str
    tipo: str
    asunto: str
    estado: str # 'pendiente', 'enviado', 'fallido', 'rebotado'
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class EmailEnviadoListResponse(BaseModel):
    data: List[EmailEnviadoResponse]
    total: int
    page: int
    size: int
