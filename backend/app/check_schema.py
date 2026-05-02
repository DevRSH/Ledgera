import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal as SessionLocal

async def check_schema():
    async with SessionLocal() as db:
        result = await db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'audit_log'"))
        columns = [row[0] for row in result.fetchall()]
        print(f"Columns in audit_log: {columns}")

if __name__ == "__main__":
    asyncio.run(check_schema())
