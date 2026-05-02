import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import String, Integer, ForeignKey, DateTime, Date, Boolean, Text, JSON, Computed
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ConciliacionBancaria(Base):
    __tablename__ = "conciliaciones_bancarias"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    año: Mapped[int] = mapped_column(Integer, nullable=False)
    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    banco: Mapped[Optional[str]] = mapped_column(String(100))
    numero_cuenta: Mapped[Optional[str]] = mapped_column(String(50))
    saldo_inicial: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_final: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="en_proceso") # 'en_proceso', 'conciliada', 'con_diferencias'
    archivo_storage_key: Mapped[Optional[str]] = mapped_column(Text)
    conciliado_por: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("usuarios.id"))
    conciliado_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    lineas: Mapped[List["LineaBancaria"]] = relationship(back_populates="conciliacion")

class LineaBancaria(Base):
    __tablename__ = "lineas_bancarias"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    conciliacion_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conciliaciones_bancarias.id"), nullable=False)
    fecha: Mapped[date] = mapped_column(Date, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(500), nullable=False)
    monto: Mapped[int] = mapped_column(Integer, nullable=False)
    saldo_banco: Mapped[Optional[int]] = mapped_column(Integer)
    movimiento_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("movimientos.id"))
    conciliada: Mapped[bool] = mapped_column(Boolean, default=False)
    observacion: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    conciliacion: Mapped["ConciliacionBancaria"] = relationship(back_populates="lineas")
