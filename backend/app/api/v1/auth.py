from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.main import limiter

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core import security
from app.core.config import settings
from app.core.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import Token, LoginRequest, LoginResponse, TOTPVerify
from app.core.dependencies import get_current_user
import pyotp


router = APIRouter()

@router.post("/login", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
    login_request: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Standard login endpoint.
    """
    result = await db.execute(select(Usuario).filter(Usuario.email == login_request.email))
    user = result.scalars().first()
    
    if not user or not security.verify_password(login_request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    elif not user.is_active:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    if user.totp_habilitado:
        # Create a temporary session token (valid for 5 minutes)
        session_token = security.create_access_token(
            subject=user.id, 
            expires_delta=timedelta(minutes=5)
        )
        return LoginResponse(require_2fa=True, session_token=session_token)

    
    access_token = security.create_access_token(subject=user.id)
    refresh_token = security.create_refresh_token(subject=user.id)
    
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.get("/me")
async def read_users_me(
    current_user: Usuario = Depends(get_current_user)
) -> Any:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nombre": current_user.nombre,
        "rol": current_user.rol
    }

@router.post("/2fa/setup")

async def setup_2fa(
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Generate TOTP secret for the user.
    """
    if current_user.totp_habilitado:
        raise HTTPException(status_code=400, detail="2FA already enabled")
    
    secret = pyotp.random_base32()
    current_user.totp_secret = secret
    await db.commit()
    
    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=current_user.email,
        issuer_name=settings.TOTP_ISSUER
    )
    
    return {"secret": secret, "uri": provisioning_uri}

@router.post("/2fa/verify")
async def verify_2fa(
    verify_data: TOTPVerify,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Verify and enable 2FA.
    """
    if not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="2FA not setup")
    
    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(verify_data.totp_code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    
    current_user.totp_habilitado = True
    await db.commit()
    return {"message": "2FA enabled successfully"}

@router.post("/login/2fa", response_model=Token)
async def login_2fa(
    verify_data: TOTPVerify,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Verify TOTP code during login flow.
    """
    try:
        payload = security.jwt.decode(
            verify_data.session_token, 
            settings.SECRET_KEY, 
            algorithms=[security.ALGORITHM]
        )
        user_id = payload.get("sub")
    except security.JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    
    result = await db.execute(select(Usuario).filter(Usuario.id == user_id))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(verify_data.totp_code):
        raise HTTPException(status_code=400, detail="Invalid TOTP code")
    
    access_token = security.create_access_token(subject=user.id)
    refresh_token = security.create_refresh_token(subject=user.id)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


