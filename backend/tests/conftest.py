import pytest
import asyncio
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import fakeredis.aioredis

import os

# Set environment to use Mock LLM
os.environ["USE_MOCK_LLM"] = "true"

from app.main import app
from app.core.config import settings
from app.worker.celery_app import celery_app

@pytest.fixture(scope="session", autouse=True)
def celery_eager():
    celery_app.conf.update(task_always_eager=True)
    yield

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def mock_dbs():
    # Mock Redis
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    
    # Mock Mongo
    fake_mongo = MagicMock()
    
    with patch("app.db.redis.get_redis", return_value=fake_redis), \
         patch("app.db.mongo.get_db", return_value=fake_mongo), \
         patch("app.core.session.get_redis", return_value=fake_redis):
        # Also patch db.connect/close in main
        with patch("app.db.mongo.db.connect"), patch("app.db.mongo.db.close"):
             yield

@pytest.fixture
def mock_browser():
    # Patch the class methods so all instances (including the singleton) are affected
    with patch("app.browser.context.BrowserManager.create_context", new_callable=AsyncMock) as mock_create, \
         patch("app.browser.context.BrowserManager.start", new_callable=AsyncMock), \
         patch("app.browser.context.BrowserManager.close", new_callable=AsyncMock):
        
        # Setup the return value of create_context
        mock_context = MagicMock()
        mock_page = MagicMock() # Page object itself is not async, but its methods are.
        # But wait, we access page props.
        
        # Configure new_page to be async and return the mock_page
        mock_context.new_page = AsyncMock(return_value=mock_page)
        mock_context.close = AsyncMock(return_value=None)
        mock_create.return_value = mock_context
        
        # Setup page methods to be async
        mock_page.goto = AsyncMock(return_value=None)
        mock_page.click = AsyncMock(return_value=None)
        mock_page.fill = AsyncMock(return_value=None)
        mock_page.evaluate = AsyncMock(return_value="Page content")
        mock_page.screenshot = AsyncMock(return_value=b"fake_screenshot")
        mock_page.close = AsyncMock(return_value=None)
        mock_page.content = AsyncMock(return_value="<html><body>Content</body></html>")
        mock_page.url = "https://google.com"
        
        yield mock_create
