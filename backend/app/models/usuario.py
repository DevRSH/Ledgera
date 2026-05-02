import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False
    )
    email: Mapped[str] = mapped_column(
        String(200), 
        unique=True, 
        index=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(
        String(200), 
        nullable=False
    )
    nombre: Mapped[str] = mapped_column(
        String(100), 
        nullable=False
    )
    rol: Mapped[str] = mapped_column(
        String(20), 
        nullable=False
    )
    totp_secret: Mapped[Optional[str]] = mapped_column(
        String(32), 
        nullable=True
    )
    totp_habilitado: Mapped[bool] = mapped_column(
        Boolean, 
        default=False
    )
    activo: Mapped[bool] = mapped_column(
        Boolean, 
        default=True
    )
    ultimo_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    # Relationships
    tenant: Mapped["Tenant"] = relationship(back_populates="usuarios")

    __table_args__ = (
        CheckConstraint(
            "rol IN ('SUPER_ADMIN', 'TESORERO', 'DIRECTIVA', 'AUDITOR', 'APODERADO')",
            name="check_usuario_rol"
        ),
    )
