from arq import create_pool
from arq.connections import RedisSettings
from app.core.config import settings

async def get_arq_pool():
    return await create_pool(RedisSettings.from_dsn(settings.REDIS_URL))
