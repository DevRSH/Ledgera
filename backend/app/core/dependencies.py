from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import ALGORITHM
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import TokenPayload
from sqlalchemy import select

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"/v1/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db)
) -> Usuario:

    # DEBUG BYPASS: Return first active user (admin) without checking token
    result = await db.execute(select(Usuario).filter(Usuario.activo == True))
    user = result.scalars().first()
    
    if not user:
        # Fallback if no user exists yet
        raise HTTPException(status_code=404, detail="No active users found. Please run seeding.")
        
    return user

