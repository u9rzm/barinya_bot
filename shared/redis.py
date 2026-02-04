import os
from redis.asyncio import Redis

redis: Redis | None = None

def get_redis() -> Redis:
    if redis is None:
        raise RuntimeError("Redis not initialized")
    return redis

async def init_redis():
    global redis
    redis = Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        password=os.getenv("REDIS_PASSWORD"),
        decode_responses=True,
    )

async def close_redis():
    if redis:
        await redis.close()
        
