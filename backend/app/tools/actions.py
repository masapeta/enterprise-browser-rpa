from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from playwright.async_api import Page
import base64

class ToolResult(BaseModel):
    success: bool
    output: Any
    error: Optional[str] = None
    screenshot_base64: Optional[str] = None
    execution_time: float = 0.0

class BaseTool:
    name: str
    description: str

    async def execute(self, page: Page, **kwargs) -> ToolResult:
        raise NotImplementedError

class OpenUrlTool(BaseTool):
    name = "open_url"
    description = "Navigate to a specific URL"

    async def execute(self, page: Page, url: str) -> ToolResult:
        try:
            await page.goto(url, wait_until="domcontentloaded")
            return ToolResult(success=True, output=f"Navigated to {url}")
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))

class ClickTool(BaseTool):
    name = "click"
    description = "Click an element by selector"

    async def execute(self, page: Page, selector: str) -> ToolResult:
        try:
            await page.click(selector)
            return ToolResult(success=True, output=f"Clicked {selector}")
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))

class TypeTextTool(BaseTool):
    name = "type_text"
    description = "Type text into an element"

    async def execute(self, page: Page, selector: str, text: str) -> ToolResult:
        try:
            await page.fill(selector, text)
            return ToolResult(success=True, output=f"Typed text into {selector}")
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))

class GetPageTextTool(BaseTool):
    name = "get_page_text"
    description = "Get the full text content of the page"

    async def execute(self, page: Page) -> ToolResult:
        try:
            # Getting visible text is usually better for LLMs
            text = await page.evaluate("document.body.innerText")
            return ToolResult(success=True, output=text[:10000]) # Truncate if huge
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))

class GetScreenshotTool(BaseTool):
    name = "get_screenshot"
    description = "Take a screenshot of the current page"

    async def execute(self, page: Page) -> ToolResult:
        try:
            screenshot_bytes = await page.screenshot(type="jpeg", quality=50)
            b64 = base64.b64encode(screenshot_bytes).decode("utf-8")
            return ToolResult(success=True, output="Screenshot taken", screenshot_base64=b64)
        except Exception as e:
            return ToolResult(success=False, output=None, error=str(e))

# Registry
TOOLS = {
    "open_url": OpenUrlTool(),
    "click": ClickTool(),
    "type_text": TypeTextTool(),
    "get_page_text": GetPageTextTool(),
    "get_screenshot": GetScreenshotTool(),
}
