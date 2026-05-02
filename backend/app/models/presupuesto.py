import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, ForeignKey, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class PresupuestoItem(Base):
    __tablename__ = "presupuesto_items"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    año: Mapped[int] = mapped_column(Integer, nullable=False)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    tipo: Mapped[str] = mapped_column(String(10), nullable=False) # 'ingreso', 'egreso'
    categoria_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("categorias_movimiento.id"))
    monto_proyectado: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[Optional[int]] = mapped_column(Integer) # NULL = anual
    descripcion: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class CierreAño(Base):
    __tablename__ = "cierres_año"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    año_cierre: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_final: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_traspasado: Mapped[int] = mapped_column(Integer, nullable=False)
    año_destino: Mapped[Optional[int]] = mapped_column(Integer)
    resumen_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    aprobado_por: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("usuarios.id"))
    aprobado_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    acta_storage_key: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
