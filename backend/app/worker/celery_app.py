import os
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Auto-discover tasks in the worker module
# Auto-discover tasks in the worker module
celery_app.autodiscover_tasks(["app.worker"])

from celery.signals import worker_process_init
from app.db.mongo import db
from app.db.redis import redis_client
import asyncio

@worker_process_init.connect
def init_worker_process(**kwargs):
    print("Initializing database connections for worker process...")
    
    # Initialize Mongo
    db.connect()
    
    # Initialize Redis (Simulating async loop if needed, or just setting up the client)
    # Since redis_client.connect() is sync-ish (just creates the client object), it's fine here.
    # But wait, redis_client.connect() uses aioredis.from_url.
    # The actual connection is lazy, so creating the object is enough.
    redis_client.connect()
    print("Worker database connections initialized.")
