from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.db.mongo import db
from app.db.redis import redis_client
from app.worker.celery_app import celery_app # Ensure Celery config is loaded

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db.connect()
    redis_client.connect()
    yield
    # Shutdown
    db.close()
    await redis_client.close()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Enterprise Agentic RPA Platform API", "status": "active"}

# Import and include routers here later
from app.api.endpoints import router as api_router
app.include_router(api_router, prefix="/api/v1")
