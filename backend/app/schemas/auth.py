from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    type: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    require_2fa: bool = False
    session_token: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

class TOTPVerify(BaseModel):
    session_token: str
    totp_code: str
