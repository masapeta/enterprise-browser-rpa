import asyncio
from typing import Dict, Any
from app.agents.planner import planner
from app.browser.context import browser_manager
from app.tools.executor import tool_executor
from app.core.session import session_manager
from app.core.logger import logger

class AgentOrchestrator:
    async def run_session(self, session_id: str, task: str):
        logger.info("session_started", session_id=session_id)
        
        # 1. Initialize Context
        context = await browser_manager.create_context()
        page = await context.new_page()
        
        # 2. Update Session State
        await session_manager.update_session(session_id, {"status": "running", "task": task})
        
        history = []
        step_count = 0
        MAX_STEPS = 20
        
        try:
            while step_count < MAX_STEPS:
                # 3. Observe
                # For now, just getting URL, we could get simplified DOM or accessibility tree
                browser_state = f"Current URL: {page.url}" 
                
                # 4. Think
                plan = await planner.plan(history, browser_state)
                
                # 5. Act
                action = plan.get("action")
                args = plan.get("args", {})
                print(f"DEBUG: Executing action {action} with args {args}")
                
                if action == "finish":
                    await session_manager.update_session(session_id, {"status": "completed", "result": args.get("final_answer")})
                    logger.info("session_completed", session_id=session_id)
                    break
                
                tool_result = await tool_executor.execute(action, page, **args)
                print(f"DEBUG: Tool result: {tool_result}")
                
                # 6. Update History & State
                step_data = {
                    "step": step_count,
                    "plan": plan,
                    "result": tool_result.dict()
                }
                history.append(step_data)
                await session_manager.add_step(session_id, step_data)
                
                step_count += 1
                
        except Exception as e:
            print(f"DEBUG: Orchestrator failed with exception: {e}")
            logger.error("session_failed", session_id=session_id, error=str(e))
            await session_manager.update_session(session_id, {"status": "failed", "error": str(e)})
        finally:
            await context.close()

agent_orchestrator = AgentOrchestrator()
