import redis
from app.core.config import settings

# Redis 连接池
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
    decode_responses=True  # 自动将响应解码为字符串
)

async def get_redis() -> redis.Redis:
    """获取 Redis 连接"""
    return redis_client 