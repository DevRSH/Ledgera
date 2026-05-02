import uuid
from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, field_validator, EmailStr
from app.core.utils import validar_rut_chileno

# --- APODERADO SCHEMAS ---

class ApoderadoBase(BaseModel):
    tipo: str # 'titular', 'suplente'
    rut: Optional[str] = None
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

class ApoderadoCreate(ApoderadoBase):
    @field_validator("rut")
    @classmethod
    def validate_rut(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return validar_rut_chileno(v)
        return v

class ApoderadoUpdate(BaseModel):
    tipo: Optional[str] = None
    rut: Optional[str] = None
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None

    @field_validator("rut")
    @classmethod
    def validate_rut(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return validar_rut_chileno(v)
        return v

class ApoderadoResponse(ApoderadoBase):
    id: uuid.UUID
    
    model_config = ConfigDict(from_attributes=True)

# --- ALUMNO SCHEMAS ---

class AlumnoBase(BaseModel):
    rut: str
    nombre: str
    apellido_paterno: str
    apellido_materno: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    activo: bool = True
    observaciones: Optional[str] = None

class AlumnoCreate(AlumnoBase):
    @field_validator("rut")
    @classmethod
    def validate_rut(cls, v: str) -> str:
        return validar_rut_chileno(v)

class AlumnoUpdate(BaseModel):
    rut: Optional[str] = None
    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    activo: Optional[bool] = None
    observaciones: Optional[str] = None

    @field_validator("rut")
    @classmethod
    def validate_rut(cls, v: Optional[str]) -> Optional[str]:
        if v:
            return validar_rut_chileno(v)
        return v

class AlumnoResponse(AlumnoBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    
    # Campos calculados o anidados solicitados
    apoderado_titular: Optional[ApoderadoResponse] = None
    estado_deuda: Optional[str] = None # Ej: "Al día", "Debe 2 cuotas"
    
    model_config = ConfigDict(from_attributes=True)

class AlumnoListResponse(BaseModel):
    data: List[AlumnoResponse]
    total: int
    page: int
    size: int
