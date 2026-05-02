import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    usuario_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("usuarios.id"))
    accion: Mapped[str] = mapped_column(String(50), nullable=False) # 'LOGIN', 'CREATE_MOVIMIENTO', etc.
    entidad_tipo: Mapped[Optional[str]] = mapped_column(String(50))
    entidad_id: Mapped[Optional[str]] = mapped_column(String(50))
    payload_antes: Mapped[Optional[dict]] = mapped_column(JSON)
    payload_despues: Mapped[Optional[dict]] = mapped_column(JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
