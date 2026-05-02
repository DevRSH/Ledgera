import uuid
from datetime import date
from typing import Optional, List
from sqlalchemy import String, Boolean, ForeignKey, Date, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Alumno(Base):
    __tablename__ = "alumnos"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    rut: Mapped[str] = mapped_column(String(12), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_paterno: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_materno: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    apoderados: Mapped[List["Apoderado"]] = relationship(back_populates="alumno", cascade="all, delete-orphan")
    pagos: Mapped[List["PagoCuota"]] = relationship(back_populates="alumno")

    __table_args__ = (
        UniqueConstraint("tenant_id", "rut", name="uq_alumno_rut"),
    )

class Apoderado(Base):
    __tablename__ = "apoderados"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    alumno_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("alumnos.id", ondelete="CASCADE"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False) # 'titular', 'suplente'
    rut: Mapped[Optional[str]] = mapped_column(String(12), nullable=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_paterno: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_materno: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    telefono: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    direccion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Relationships
    alumno: Mapped["Alumno"] = relationship(back_populates="apoderados")

    __table_args__ = (
        CheckConstraint("tipo IN ('titular', 'suplente')", name="check_apoderado_tipo"),
    )
