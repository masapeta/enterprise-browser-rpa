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
    
    channel = f"session_updates:{session_id}"
    await pubsub.subscribe(channel)
    input_channel = f"session_input:{session_id}"

    async def receive_from_client():
        try:
            while True:
                data = await websocket.receive_text()
                await redis.publish(input_channel, data)
        except WebSocketDisconnect:
            pass
        except Exception as e:
            pass

    async def send_to_client():
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    data = message["data"]
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                    try:
                        await websocket.send_text(data)
                    except Exception:
                        break
                await asyncio.sleep(0.05)
        except WebSocketDisconnect:
            pass
        except Exception as e:
            pass

    send_task = asyncio.create_task(send_to_client())
    recv_task = asyncio.create_task(receive_from_client())
    
    done, pending = await asyncio.wait(
        [send_task, recv_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    
    await pubsub.unsubscribe(channel)
