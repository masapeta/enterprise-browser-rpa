from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import json

from app.core.session import session_manager
from app.worker.tasks import run_agent_task
from app.db.redis import get_redis

router = APIRouter()

class CreateSessionRequest(BaseModel):
    task: str

class SessionResponse(BaseModel):
    session_id: str
    status: str

@router.post("/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest):
    session_id = await session_manager.create_session()
    
    # Trigger Worker
    run_agent_task.delay(session_id, request.task)
    
    return SessionResponse(session_id=session_id, status="ready")

@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    data = await session_manager.get_session(session_id)
    if not data:
        raise HTTPException(status_code=404, detail="Session not found")
    return data

@router.websocket("/sessions/{session_id}/ws")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    redis = await get_redis()
    pubsub = redis.pubsub()
    
    # Subscribe to session updates (implementation detail: Orchestrator needs to publish events)
    # For now, we'll just poll session state or assume a channel exists
    channel = f"session_updates:{session_id}"
    await pubsub.subscribe(channel)

    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                await websocket.send_text(message["data"])
            await asyncio.sleep(0.1)
    except WebSocketDisconnect:
        await pubsub.unsubscribe(channel)
