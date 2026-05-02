import uuid
from datetime import date, datetime
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, Text, DateTime, Date, Boolean, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ComprobantePago(Base):
    __tablename__ = "comprobantes_pago"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    folio: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    pago_cuota_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("pagos_cuota.id"), nullable=False)
    alumno_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("alumnos.id"), nullable=False)
    año: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    monto: Mapped[int] = mapped_column(Integer, nullable=False)
    fecha_pago: Mapped[date] = mapped_column(Date, nullable=False)
    recibido_por: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    recibido_por_nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    qr_verification_url: Mapped[str] = mapped_column(Text, nullable=False)
    pdf_storage_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    hash_pdf: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    anulado: Mapped[bool] = mapped_column(Boolean, default=False)
    anulado_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    motivo_anulacion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    pago: Mapped["PagoCuota"] = relationship()
    alumno: Mapped["Alumno"] = relationship()

    __table_args__ = (
        Index("idx_comprobantes_folio", "folio"),
    )
