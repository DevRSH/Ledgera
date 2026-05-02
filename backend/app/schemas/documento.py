import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class DocumentoResponse(BaseModel):
    id: uuid.UUID
    nombre_original: str
    mime_type: str
    tamaño_bytes: int
    tipo_documento: str # 'boleta', 'factura', etc.
    subido_por_nombre: Optional[str] = None # Se poblará desde la relación Usuario
    created_at: Optional[datetime] = None
    
    # NUNCA incluir storage_key ni hash en la response pública
    
    model_config = ConfigDict(from_attributes=True)

class DocumentoUploadResponse(BaseModel):
    id: uuid.UUID
    folio: Optional[str] = None # Si el documento genera un folio o está asociado a uno
    download_url: str

class DocumentoListResponse(BaseModel):
    data: List[DocumentoResponse]
    total: int
    page: int
    size: int
