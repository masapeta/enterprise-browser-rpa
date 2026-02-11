import time
from app.tools.actions import TOOLS, ToolResult
from app.core.logger import logger
from playwright.async_api import Page

class ToolExecutor:
    async def execute(self, tool_name: str, page: Page, **kwargs) -> ToolResult:
        start_time = time.time()
        tool = TOOLS.get(tool_name)
        
        if not tool:
            return ToolResult(success=False, output=None, error=f"Tool {tool_name} not found")

        try:
            logger.info("executing_tool", tool=tool_name, args=kwargs)
            result = await tool.execute(page, **kwargs)
            
            # Auto-screenshot on failure or significant action could be added here
            if not result.screenshot_base64 and not result.success:
                 # Try to take a screenshot on failure
                 try:
                     import base64
                     screenshot_bytes = await page.screenshot(type="jpeg", quality=50)
                     result.screenshot_base64 = base64.b64encode(screenshot_bytes).decode("utf-8")
                 except:
                     pass

        except Exception as e:
            logger.error("tool_execution_failed", tool=tool_name, error=str(e))
            result = ToolResult(success=False, output=None, error=str(e))
        
        result.execution_time = time.time() - start_time
        logger.info("tool_executed", tool=tool_name, success=result.success, duration=result.execution_time)
        return result

tool_executor = ToolExecutor()
