from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class SharedBase(DeclarativeBase):
    """Base for all models, including append-only ones"""
    
    # Timestamps - Only creation for all
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        comment="Fecha de creación"
    )

class Base(SharedBase):
    """Base for mutable models with soft delete and update tracking"""
    __abstract__ = True
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(),
        comment="Fecha de última actualización"
    )
    
    # Soft delete
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Fecha de eliminación lógica"
    )
