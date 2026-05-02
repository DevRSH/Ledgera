import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Date, Boolean, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Vale(Base):
    __tablename__ = "vales"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    folio: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False) # 'ingreso', 'egreso'
    movimiento_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movimientos.id"), nullable=False)
    concepto: Mapped[str] = mapped_column(String(500), nullable=False)
    monto: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    recibe_nombre: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    entrega_nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_storage_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    anulado: Mapped[bool] = mapped_column(Boolean, default=False)
    anulado_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    motivo_anulacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    movimiento: Mapped["Movimiento"] = relationship()

    __table_args__ = (
        CheckConstraint("tipo IN ('ingreso', 'egreso')", name="check_vale_tipo"),
        Index("idx_vales_folio", "folio"),
    )
