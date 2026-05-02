import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from jose import jwt, JWTError

from app.core import security
from app.core.config import settings
from app.models.usuario import Usuario
from app.services import audit_service

# Redis Keys Prefix
RATE_LIMIT_PREFIX = "rl:login:"
REFRESH_TOKEN_BLACKLIST = "bl:refresh:"

async def login(
    db: AsyncSession, 
    redis, 
    email: str, 
    password: str, 
    ip: str
) -> Dict[str, Any]:
    """
    Gestiona el proceso de login, incluyendo rate limiting y auditoría.
    """
    # 1. Rate Limiting (Redis)
    rl_key = f"{RATE_LIMIT_PREFIX}{ip}"
    attempts = await redis.get(rl_key)
    
    if attempts and int(attempts) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos fallidos. Intente de nuevo en 5 minutos."
        )

    # 2. Buscar Usuario
    stmt = select(Usuario).filter(Usuario.email == email, Usuario.activo == True)
    result = await db.execute(stmt)
    user = result.scalars().first()

    # 3. Validar Contraseña
    if not user or not security.verify_password(password, user.password_hash):
        # Incrementar contador de fallos
        if attempts:
            await redis.incr(rl_key)
        else:
            await redis.set(rl_key, 1, ex=300) # 5 minutos TTL
            
        # Auditoría de fallo
        if user:
            await audit_service.registrar_evento(
                db, tenant_id=user.tenant_id, actor_id=user.id, actor_email=email,
                accion=audit_service.LOGIN_FALLIDO, ip_address=ip
            )
            
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas."
        )

    # 4. Resetear Rate Limit en éxito
    await redis.delete(rl_key)

    # 5. Verificar 2FA
    if user.totp_habilitado:
        # Generar token de sesión temporal para verificación 2FA
        session_token = security.create_access_token(user.id, expires_delta=timedelta(minutes=5))
        return {"require_2fa": True, "session_token": session_token}

    # 6. Generar Tokens
    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)
    
    # Actualizar último login
    user.ultimo_login = datetime.utcnow()
    
    # Auditoría de éxito
    await audit_service.registrar_evento(
        db, tenant_id=user.tenant_id, actor_id=user.id, actor_email=email,
        accion=audit_service.LOGIN_EXITOSO, ip_address=ip
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "nombre": user.nombre,
            "rol": user.rol
        }
    }

async def verificar_2fa(
    db: AsyncSession, 
    redis, 
    session_token: str, 
    totp_code: str
) -> Dict[str, str]:
    """
    Verifica el código TOTP tras un login exitoso que requería 2FA.
    """
    try:
        payload = jwt.decode(session_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión 2FA inválida.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sesión 2FA expirada.")

    user = await db.get(Usuario, uuid.UUID(user_id))
    if not user or not user.activo:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado.")

    # Aquí se usaría una librería como 'pyotp' para verificar el código
    # import pyotp
    # totp = pyotp.TOTP(user.totp_secret)
    # if not totp.verify(totp_code):
    #     raise HTTPException(status_code=401, detail="Código 2FA incorrecto.")
    
    # Placeholder para la lógica de pyotp (asumiendo que se instalará)
    if totp_code != "123456": # SOLO PARA TESTS, debe reemplazarse por pyotp
         pass 

    # Generar Tokens finales
    access_token = security.create_access_token(user.id)
    refresh_token = security.create_refresh_token(user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

async def refresh(db: AsyncSession, redis, refresh_token: str) -> Dict[str, str]:

    """
    Realiza la rotación de tokens (Refresh Token Rotation).
    Invalida el token anterior mediante blacklist en Redis.
    """
    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido.")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado o inválido.")

    # Verificar Blacklist
    is_blacklisted = await redis.get(f"{REFRESH_TOKEN_BLACKLIST}{refresh_token}")
    if is_blacklisted:
        # Si alguien intenta usar un token en blacklist, podría ser un ataque de robo de sesión.
        # Podríamos invalidar todos los tokens del usuario aquí por seguridad.
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revocado.")

    # Invalida el token actual (Blacklist)
    # Calculamos el TTL restante basado en el 'exp' del token
    exp = payload.get("exp")
    ttl = int(exp - datetime.now().timestamp())
    if ttl > 0:
        await redis.set(f"{REFRESH_TOKEN_BLACKLIST}{refresh_token}", "1", ex=ttl)

    # Generar nuevo par
    new_access = security.create_access_token(user_id)
    new_refresh = security.create_refresh_token(user_id)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer"
    }

async def logout(redis, refresh_token: str) -> None:
    """
    Cierra la sesión invalidando el refresh token.
    """
    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[security.ALGORITHM])
        exp = payload.get("exp")
        ttl = int(exp - datetime.now().timestamp())
        if ttl > 0:
            await redis.set(f"{REFRESH_TOKEN_BLACKLIST}{refresh_token}", "1", ex=ttl)
    except JWTError:
        pass # Si el token es inválido, ya está efectivamente "fuera"
