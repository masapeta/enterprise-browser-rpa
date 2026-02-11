import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.core.session import session_manager

@pytest.mark.asyncio
async def test_health_check():
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "active"

@pytest.mark.asyncio
async def test_create_session(mock_browser):
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/api/v1/sessions", json={"task": "test task"})
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["status"] == "ready"
    
    # Verify session in (mock) redis
    session = await session_manager.get_session(data["session_id"])
    assert session is not None
    assert session["status"] == "ready"

@pytest.mark.asyncio
async def test_concurrency_simulation():
    """
    Simulate creating multiple sessions to ensure no ID collision or state bleed.
    """
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        tasks = [ac.post("/api/v1/sessions", json={"task": f"task {i}"}) for i in range(10)]
        responses = await asyncio.gather(*tasks)
        
    session_ids = set()
    for res in responses:
        assert res.status_code == 200
        session_ids.add(res.json()["session_id"])
        
    assert len(session_ids) == 10
