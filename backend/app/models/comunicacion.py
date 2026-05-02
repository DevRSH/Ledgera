import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, ForeignKey, DateTime, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class PlantillaEmail(Base):
    __tablename__ = "plantillas_email"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False) # 'comprobante_pago', 'estado_cuenta', etc.
    asunto_template: Mapped[str] = mapped_column(String(300), nullable=False)
    cuerpo_html_template: Mapped[str] = mapped_column(Text, nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "tipo IN ('comprobante_pago', 'estado_cuenta', 'recordatorio_cuota', 'bienvenida')",
            name="check_plantilla_tipo"
        ),
    )

class EmailEnviado(Base):
    __tablename__ = "emails_enviados"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    alumno_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("alumnos.id"), nullable=True)
    apoderado_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("apoderados.id"), nullable=True)
    destinatario_email: Mapped[str] = mapped_column(String(200), nullable=False)
    destinatario_nombre: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    asunto: Mapped[str] = mapped_column(String(300), nullable=False)
    cuerpo_html: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente") # 'pendiente', 'enviado', 'fallido', 'rebotado'
    resend_message_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    error_detalle: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    adjunto_storage_key: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    enviado_por: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("usuarios.id"), nullable=True)
    intentos: Mapped[int] = mapped_column(default=0)
    ultimo_intento: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "estado IN ('pendiente', 'enviado', 'fallido', 'rebotado')",
            name="check_email_estado"
        ),
    )
