import aioredis
from app.core.config import settings

# Redis 连接池
redis_client = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True  # 自动将响应解码为字符串
)

async def get_redis() -> aioredis.Redis:
    """获取 Redis 连接"""
    return redis_client 