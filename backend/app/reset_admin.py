import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.core.database import AsyncSessionLocal as SessionLocal
from app.models.usuario import Usuario
from app.core import security

async def reset_admin():
    async with SessionLocal() as db:
        result = await db.execute(select(Usuario).filter(Usuario.email == "admin@ledgera.com"))
        admin = result.scalars().first()
        
        if admin:
            print("Resetting password for admin@ledgera.com")
            admin.password_hash = security.get_password_hash("admin123456")
            admin.activo = True
            await db.commit()
            print("Password reset successfully.")
        else:
            print("Admin user not found.")

if __name__ == "__main__":
    asyncio.run(reset_admin())
