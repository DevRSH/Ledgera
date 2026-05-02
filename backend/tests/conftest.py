import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.models.base import SharedBase
from app.core.database import get_db
from app.main import app
from httpx import AsyncClient, ASGITransport

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(SharedBase.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def db(engine):
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest_asyncio.fixture
async def client(db):
    def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def user_tesorero(db: AsyncSession):
    user = Usuario(
        id=uuid.uuid4(), email="tesorero@test.com", password_hash="hash",
        rol="TESORERO", tenant_id=uuid.uuid4(), activo=True
    )
    db.add(user)
    await db.commit()
    return user

@pytest_asyncio.fixture
async def user_auditor(db: AsyncSession):
    user = Usuario(
        id=uuid.uuid4(), email="auditor@test.com", password_hash="hash",
        rol="AUDITOR", tenant_id=uuid.uuid4(), activo=True
    )
    db.add(user)
    await db.commit()
    return user

@pytest_asyncio.fixture
async def user_directiva(db: AsyncSession):
    user = Usuario(
        id=uuid.uuid4(), email="directiva@test.com", password_hash="hash",
        rol="DIRECTIVA", tenant_id=uuid.uuid4(), activo=True
    )
    db.add(user)
    await db.commit()
    return user

@pytest_asyncio.fixture
async def user_apoderado(db: AsyncSession):
    user = Usuario(
        id=uuid.uuid4(), email="apoderado@test.com", password_hash="hash",
        rol="APODERADO", tenant_id=uuid.uuid4(), activo=True
    )
    db.add(user)
    await db.commit()
    return user

from app.core.security import create_access_token
from datetime import timedelta

@pytest.fixture
def token_tesorero(user_tesorero):
    return create_access_token(user_tesorero.id, expires_delta=timedelta(minutes=10))

@pytest.fixture
def token_auditor(user_auditor):
    return create_access_token(user_auditor.id, expires_delta=timedelta(minutes=10))

@pytest.fixture
def token_directiva(user_directiva):
    return create_access_token(user_directiva.id, expires_delta=timedelta(minutes=10))

@pytest.fixture
def token_apoderado(user_apoderado):
    return create_access_token(user_apoderado.id, expires_delta=timedelta(minutes=10))
