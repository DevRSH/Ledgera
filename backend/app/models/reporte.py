import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class ReporteJob(Base):
    __tablename__ = "reporte_jobs"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(30), nullable=False)
    parametros: Mapped[Optional[dict]] = mapped_column(JSON)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente") # 'pendiente', 'procesando', 'completado', 'error'
    resultado_storage_key: Mapped[Optional[str]] = mapped_column(Text)
    resultado_url: Mapped[Optional[str]] = mapped_column(Text)
    error_detalle: Mapped[Optional[str]] = mapped_column(Text)
    solicitado_por: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completado_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
