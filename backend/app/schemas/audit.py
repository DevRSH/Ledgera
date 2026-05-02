import uuid
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, ConfigDict

class AuditLogResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    usuario_id: Optional[uuid.UUID] = None
    accion: str
    entidad_tipo: Optional[str] = None
    entidad_id: Optional[str] = None
    payload_antes: Optional[Any] = None
    payload_despues: Optional[Any] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
