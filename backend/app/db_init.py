import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import SessionLocal
from app.models.tenant import Tenant
from app.models.usuario import Usuario
from app.core import security

async def init_first_user():
    async with SessionLocal() as db:
        # Check if the specific admin user exists
        result = await db.execute(select(Usuario).filter(Usuario.email == "admin@ledgera.com"))
        admin = result.scalars().first()
        
        if not admin:
            print("🌱 El usuario administrador no existe. Iniciando creación...")
            
            # Check if any tenant exists, or create one
            result = await db.execute(select(Tenant).limit(1))
            tenant = result.scalars().first()
            
            if not tenant:
                print("🏢 Creando tenant inicial...")
                tenant = Tenant(
                    nombre="Curso Demo 2026",
                    año=2026,
                    nivel="8° Básico",
                    colegio="Colegio Ledgera"
                )
                db.add(tenant)
                await db.flush()
            
            print("👤 Creando usuario administrador: admin@ledgera.com")
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
            print("✅ Usuario administrador creado con éxito.")
        else:
            print("ℹ️ El usuario administrador ya existe. Saltando creación.")


if __name__ == "__main__":
    asyncio.run(init_first_user())
