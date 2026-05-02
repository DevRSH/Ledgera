import uuid
from datetime import date
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Date, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ConfiguracionCuota(Base):
    __tablename__ = "configuracion_cuotas"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    año: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    monto: Mapped[int] = mapped_column(Integer, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    fecha_vencimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "año", "mes", name="uq_cuota_mes"),
        CheckConstraint("mes BETWEEN 1 AND 12", name="check_cuota_mes"),
        CheckConstraint("monto >= 0", name="check_cuota_monto"),
    )

class PagoCuota(Base):
    __tablename__ = "pagos_cuota"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    alumno_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("alumnos.id", ondelete="CASCADE"), nullable=False)
    año: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    monto_pagado: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_pago: Mapped[date] = mapped_column(Date, nullable=False)
    movimiento_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("movimientos.id"), nullable=True)
    registrado_por: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    alumno: Mapped["Alumno"] = relationship(back_populates="pagos")
    movimiento: Mapped[Optional["Movimiento"]] = relationship()

    __table_args__ = (
        UniqueConstraint("tenant_id", "alumno_id", "año", "mes", name="uq_pago_mes"),
        CheckConstraint("mes BETWEEN 1 AND 12", name="check_pago_mes"),
        CheckConstraint("monto_pagado > 0", name="check_pago_monto"),
    )

class Condonacion(Base):
    __tablename__ = "condonaciones"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    alumno_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("alumnos.id", ondelete="CASCADE"), nullable=False)
    año: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True) # NULL = año completo
    motivo: Mapped[str] = mapped_column(String(500), nullable=False)
    autorizado_por: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("mes IS NULL OR (mes BETWEEN 1 AND 12)", name="check_condonacion_mes"),
    )
    
    # Relationships
    alumno: Mapped["Alumno"] = relationship()
