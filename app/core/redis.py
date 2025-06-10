import os
import aioredis

# Redis 连接池
redis_client = aioredis.from_url(
    f"redis://{os.getenv('REDIS_HOST','localhost')}:{os.getenv('REDIS_PORT','6379')}",
    db=os.getenv('REDIS_DB','0'),
    password=os.getenv('REDIS_PASSWORD',''),
    decode_responses=True  # 自动将响应解码为字符串
)

async def get_redis() -> aioredis.Redis:
    """获取 Redis 连接"""
    return redis_client 