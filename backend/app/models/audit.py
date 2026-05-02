import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import BigInteger, String, JSON, DateTime, func, Index, Computed
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import SharedBase

class AuditLog(SharedBase):
    __tablename__ = "audit_log"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    tenant_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    actor_id: Mapped[uuid.UUID] = mapped_column(nullable=False, index=True)
    actor_email: Mapped[str] = mapped_column(String(200), nullable=False)
    accion: Mapped[str] = mapped_column(String(100), nullable=False)
    entidad: Mapped[str] = mapped_column(String(50), nullable=False)
    entidad_id: Mapped[str] = mapped_column(String(100), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True) # IPv6 ready
    payload_antes: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    payload_despues: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


    __table_args__ = (
        Index("idx_audit_entidad", "entidad", "entidad_id"),
    )
