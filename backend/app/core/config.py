from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "Ledgera"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str
    REDIS_URL: str
    
    # Security
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TOTP_ISSUER: str = "Ledgera"
    
    # Storage (Cloudflare R2)
    R2_BUCKET_NAME: str = "tesoapp-docs"
    R2_ENDPOINT_URL: Optional[str] = None
    R2_ACCESS_KEY_ID: Optional[str] = None
    R2_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Email (Resend)
    RESEND_API_KEY: Optional[str] = None
    
    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    def __init__(self, **values):
        super().__init__(**values)
        # Fix for Railway/Render/Heroku Postgres URLs
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        elif self.DATABASE_URL.startswith("postgresql://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

settings = Settings()

