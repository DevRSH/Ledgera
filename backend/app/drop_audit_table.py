import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal as SessionLocal

async def fix_schema():
    async with SessionLocal() as db:
        print("Dropping audit_log table...")
        await db.execute(text("DROP TABLE IF EXISTS audit_log CASCADE"))
        await db.commit()
        print("Table dropped.")

if __name__ == "__main__":
    asyncio.run(fix_schema())
