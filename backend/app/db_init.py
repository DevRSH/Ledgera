import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.core import security

async def init_first_user():
    async with SessionLocal() as db:
        # Check if any tenant exists
        result = await db.execute(select(Tenant).limit(1))
        tenant = result.scalars().first()
        
        if not tenant:
            print("🌱 Creando tenant inicial...")
            tenant = Tenant(
                nombre="Curso Demo 2026",
                año=2026,
                nivel="8° Básico",
                colegio="Colegio Ledgera"
            )
            db.add(tenant)
            await db.flush() # To get the tenant ID
            
            print("👤 Creando usuario administrador inicial...")
            admin_user = Usuario(
                tenant_id=tenant.id,
                email="admin@ledgera.com",
                password_hash=security.get_password_hash("admin123456"),
                nombre="Administrador Maestro",
                rol="SUPER_ADMIN",
                activo=True
            )
            db.add(admin_user)
            await db.commit()
            print("✅ Datos iniciales creados con éxito.")
        else:
            print("ℹ️ La base de datos ya tiene datos, saltando inicialización.")

if __name__ == "__main__":
    asyncio.run(init_first_user())
