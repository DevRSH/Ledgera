import asyncio
from arq.connections import RedisSettings
from app.core.config import settings
from app.services.email_service import email_service
from app.core.database import AsyncSessionLocal
from app.models.comunicacion import EmailEnviado

async def startup(ctx):
    ctx['email_service'] = email_service

async def shutdown(ctx):
    pass

async def enviar_email_task(ctx, email_id: str):
    async with AsyncSessionLocal() as db:
        email = await db.get(EmailEnviado, email_id)
        if not email:
            return
            
        try:
            # Logic to send the email
            # This is a simplified version for the sprint
            email.estado = "enviado"
            await db.commit()
        except Exception as e:
            email.estado = "fallido"
            email.error_detalle = str(e)
            await db.commit()

class WorkerSettings:
    functions = [enviar_email_task]
    redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)
    on_startup = startup
    on_shutdown = shutdown
