import uuid
from datetime import date, datetime
from typing import Optional, List

from sqlalchemy import String, Integer, ForeignKey, Date, DateTime, Boolean, CheckConstraint, Index, UniqueConstraint

from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class CategoriaMovimiento(Base):
    __tablename__ = "categorias_movimiento"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False) # 'ingreso', 'egreso', 'ambos'
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True) # Hex color
    activa: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("tenant_id", "nombre", name="uq_categoria_nombre"),
        CheckConstraint("tipo IN ('ingreso', 'egreso', 'ambos')", name="check_categoria_tipo"),
    )

class Movimiento(Base):
    __tablename__ = "movimientos"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False) # 'ingreso', 'egreso'
    monto: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    categoria_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("categorias_movimiento.id"), nullable=True)
    forma_pago: Mapped[Optional[str]] = mapped_column(String(20), nullable=True) # 'efectivo', 'transferencia', etc.
    referencia_bancaria: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    registrado_por: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    
    # Anulación (Append-only style)
    anulado: Mapped[bool] = mapped_column(Boolean, default=False)
    anulado_por: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    anulado_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    motivo_anulacion: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    categoria: Mapped[Optional["CategoriaMovimiento"]] = relationship()
    registrador: Mapped["Usuario"] = relationship(foreign_keys=[registrado_por])
    anulador: Mapped[Optional["Usuario"]] = relationship(foreign_keys=[anulado_por])
    documentos: Mapped[List["Documento"]] = relationship(
        secondary="movimiento_documentos", back_populates="movimientos"
    )


    __table_args__ = (
        CheckConstraint("tipo IN ('ingreso', 'egreso')", name="check_movimiento_tipo"),
        CheckConstraint("monto > 0", name="check_movimiento_monto"),
        CheckConstraint("forma_pago IN ('efectivo','transferencia','cheque','otro')", name="check_movimiento_forma_pago"),
        Index("idx_movimientos_tenant_fecha", "tenant_id", "fecha"),
        Index("idx_movimientos_tipo", "tenant_id", "tipo"),
    )
