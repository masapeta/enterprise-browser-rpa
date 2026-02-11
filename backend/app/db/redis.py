import redis.asyncio as aioredis
from app.core.config import settings

class RedisClient:
    redis: aioredis.Redis = None

    def connect(self):
        self.redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        print(f"Connected to Redis at {settings.REDIS_URL}")

    async def close(self):
        if self.redis:
            await self.redis.close()
            print("Redis connection closed")

redis_client = RedisClient()

async def get_redis():
    return redis_client.redis
