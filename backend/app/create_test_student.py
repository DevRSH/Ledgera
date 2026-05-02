import asyncio
import uuid
from app.models.alumno import Alumno, Apoderado
from app.models.usuario import Usuario
from sqlalchemy import select
from app.core.database import AsyncSessionLocal as SessionLocal
from app.services import audit_service

async def create_test_student():
    async with SessionLocal() as db:
        # Get admin user
        result = await db.execute(select(Usuario).filter(Usuario.email == "admin@ledgera.com"))
        admin = result.scalars().first()
        
        if not admin:
            print("Admin user not found.")
            return

        # Use "rut 15" as requested
        rut_test = "15.000.000-1"
        
        # Check if already exists
        result = await db.execute(select(Alumno).filter(Alumno.rut == rut_test))
        if result.scalars().first():
            print(f"Student with RUT {rut_test} already exists.")
            return

        print(f"Creating student with RUT {rut_test}...")
        
        new_alumno = Alumno(
            id=uuid.uuid4(),
            tenant_id=admin.tenant_id,
            rut=rut_test,
            nombre="Alumno",
            apellido_paterno="Test",
            apellido_materno="Quinze",
            activo=True
        )
        db.add(new_alumno)
        await db.flush()
        
        # Audit
        await audit_service.registrar_evento(
            db, 
            tenant_id=admin.tenant_id, 
            actor_id=admin.id,
            actor_email=admin.email, 
            accion=audit_service.CREATE_ALUMNO,
            entidad="Alumno", 
            entidad_id=str(new_alumno.id),
            payload_despues={"rut": rut_test}
        )
        
        await db.commit()
        print(f"Student created successfully with ID: {new_alumno.id}")

if __name__ == "__main__":
    asyncio.run(create_test_student())
