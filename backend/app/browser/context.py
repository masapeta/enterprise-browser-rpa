from playwright.async_api import async_playwright, Browser, Playwright, BrowserContext
from app.core.config import settings
from app.core.logger import logger

class BrowserManager:
    playwright: Playwright = None
    browser: Browser = None

    async def start(self):
        if not self.playwright:
            self.playwright = await async_playwright().start()
            logger.info("Playwright started")
        
        if not self.browser:
            # Headless=True for docker usually, but requirements say Headful mode support.
            # We can control this via env var or simply default to Headless=True for server.
            # For "Live View", we might need to stream screenshots/video anyway.
            self.browser = await self.playwright.chromium.launch(
                headless=settings.HEADLESS, 
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            logger.info("Browser launched")

    async def create_context(self) -> BrowserContext:
        if not self.browser:
            await self.start()
        
        context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir="videos/" # Optional for debugging
        )
        return context

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

browser_manager = BrowserManager()
