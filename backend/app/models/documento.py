import uuid
from typing import List
from sqlalchemy import String, Integer, ForeignKey, Text, CheckConstraint, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

# Pivot table for Movimiento <-> Documento
movimiento_documentos = Table(
    "movimiento_documentos",
    Base.metadata,
    Column("movimiento_id", ForeignKey("movimientos.id"), primary_key=True),
    Column("documento_id", ForeignKey("documentos.id"), primary_key=True),
)

class Documento(Base):
    __tablename__ = "documentos"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    nombre_original: Mapped[str] = mapped_column(String(300), nullable=False)
    nombre_storage: Mapped[str] = mapped_column(String(300), nullable=False)
    storage_url: Mapped[str] = mapped_column(Text, nullable=False)
    storage_key: Mapped[str] = mapped_column(Text, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    tamaño_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(30), nullable=False) # 'boleta', 'factura', etc.
    hash_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    subido_por: Mapped[uuid.UUID] = mapped_column(ForeignKey("usuarios.id"), nullable=False)

    # Relationships
    movimientos: Mapped[List["Movimiento"]] = relationship(
        secondary=movimiento_documentos, back_populates="documentos"
    )

    __table_args__ = (
        CheckConstraint(
            "tipo_documento IN ('boleta', 'factura', 'estado_cuenta_bancario', 'acta_reunion', 'foto', 'otro')",
            name="check_tipo_documento"
        ),
    )
