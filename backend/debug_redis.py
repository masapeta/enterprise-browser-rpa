import sys
import asyncio
from redis.asyncio import Redis as AsyncRedis
from redis import Redis
from celery import Celery

# Configuration to test
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/0"

print(f"--- Testing Redis Connection to {BROKER_URL} ---")

def test_sync_redis():
    print("\n1. Testing Synchronous Redis (redis-py)...")
    try:
        r = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, socket_connect_timeout=2)
        r.ping()
        print("✅ Sync Redis: Connected successfully!")
    except Exception as e:
        print(f"❌ Sync Redis Failed: {e}")

async def test_async_redis():
    print("\n2. Testing Asynchronous Redis (aioredis)...")
    try:
        r = AsyncRedis.from_url(BROKER_URL, decode_responses=True, socket_connect_timeout=2)
        await r.ping()
        print("✅ Async Redis: Connected successfully!")
        await r.close()
    except Exception as e:
        print(f"❌ Async Redis Failed: {e}")

def test_celery_connection():
    print("\n3. Testing Celery Broker Connection...")
    try:
        app = Celery("test", broker=BROKER_URL)
        with app.connection_for_write() as conn:
            conn.connect()
            print("✅ Celery Broker: Connected successfully!")
    except Exception as e:
        print(f"❌ Celery Broker Failed: {e}")

if __name__ == "__main__":
    test_sync_redis()
    asyncio.run(test_async_redis())
    test_celery_connection()
    print("\n--- End of Debug ---")
