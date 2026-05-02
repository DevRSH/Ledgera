import uuid
from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class Tenant(Base):
    __tablename__ = "tenants"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, 
        default=uuid.uuid4,
        comment="ID único del tenant"
    )
    nombre: Mapped[str] = mapped_column(
        String(100), 
        nullable=False,
        comment="Nombre del curso (ej: 5° Básico B)"
    )
    año: Mapped[int] = mapped_column(
        Integer, 
        nullable=False,
        comment="Año académico"
    )
    nivel: Mapped[str] = mapped_column(
        String(20), 
        nullable=False,
        comment="Nivel (ej: 5B, 3A)"
    )
    colegio: Mapped[str] = mapped_column(
        String(200), 
        nullable=False,
        comment="Nombre del establecimiento"
    )
    activo: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        comment="Indica si el tenant está operativo"
    )

    # Relationships
    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="tenant",
        cascade="all, delete-orphan"
    )
