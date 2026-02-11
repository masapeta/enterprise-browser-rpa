import uuid
import json
import time
from typing import Optional, Dict, Any
from app.db.redis import get_redis

class SessionManager:
    PREFIX = "session:"
    TTL = 3600  # 1 hour expiration

    async def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        redis = await get_redis()
        initial_state = {
            "session_id": session_id,
            "created_at": time.time(),
            "status": "ready",
            "steps": [],
            "memory": {}
        }
        await redis.setex(
            f"{self.PREFIX}{session_id}",
            self.TTL,
            json.dumps(initial_state)
        )
        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        redis = await get_redis()
        data = await redis.get(f"{self.PREFIX}{session_id}")
        if data:
            return json.loads(data)
        return None

    async def update_session(self, session_id: str, updates: Dict[str, Any]):
        redis = await get_redis()
        # Optimistic locking or simple update? For now, simple get-set
        # In prod, use Lua script or watch for atomicity
        current = await self.get_session(session_id)
        if current:
            current.update(updates)
            current["updated_at"] = time.time()
            await redis.setex(
                f"{self.PREFIX}{session_id}",
                self.TTL,
                json.dumps(current)
            )

    async def add_step(self, session_id: str, step_data: Dict[str, Any]):
        redis = await get_redis()
        current = await self.get_session(session_id)
        if current:
            if "steps" not in current:
                current["steps"] = []
            current["steps"].append(step_data)
            await redis.setex(
                f"{self.PREFIX}{session_id}",
                self.TTL,
                json.dumps(current)
            )

session_manager = SessionManager()
