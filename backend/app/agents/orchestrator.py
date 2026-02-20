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
        
        try:
            import json
            from app.db.redis import get_redis
            redis = await get_redis()
            pubsub = redis.pubsub()
            await pubsub.subscribe(f"session_input:{session_id}")

            while True:
                step_count = 0
                MAX_STEPS = 20
                
                while step_count < MAX_STEPS:
                    # 3. Observe
                    # For now, just getting URL, we could get simplified DOM or accessibility tree
                    browser_state = f"Current URL: {page.url}" 
                    
                    # 4. Think
                    plan = await planner.plan(task, history, browser_state)
                    print(f"DEBUG: Plan received: {plan}")
                    
                    # 5. Act
                    action = plan.get("action")
                    args = plan.get("args", {})
                    print(f"DEBUG: Executing action {action} with args {args}")
                    
                    if action == "finish":
                        final_answer = args.get("final_answer", "Task complete.")
                        await session_manager.update_session(session_id, {"status": "completed", "result": final_answer})
                        logger.info("session_completed", session_id=session_id)
                        
                        chat_msg = {"type": "chat", "sender": "agent", "message": final_answer}
                        await redis.publish(f"session_updates:{session_id}", json.dumps(chat_msg))
                        break
                    
                    tool_result = await tool_executor.execute(action, page, **args)
                    print(f"DEBUG: Tool result: {tool_result}")
                    
                    # 5.5 Capture Screenshot & Stream
                    try:
                        screenshot_bytes = await page.screenshot(type="jpeg", quality=50)
                        import base64
                        b64_img = base64.b64encode(screenshot_bytes).decode('utf-8')
                        img_data = f"data:image/jpeg;base64,{b64_img}"
                        
                        await redis.publish(f"session_updates:{session_id}", json.dumps({"type": "image", "data": img_data}))
                    except Exception as sc_err:
                        print(f"DEBUG: Screenshot failed: {sc_err}")

                    # 6. Update History & State
                    step_data = {
                        "step": step_count,
                        "plan": plan,
                        "result": tool_result.dict()
                    }
                    history.append(step_data)
                    await session_manager.add_step(session_id, step_data)
                    
                    step_count += 1

                # Wait for next task/message from user
                await session_manager.update_session(session_id, {"status": "waiting_for_input"})
                
                new_task = None
                while True:
                    message = await pubsub.get_message(ignore_subscribe_messages=True)
                    if message:
                        data = message["data"]
                        if isinstance(data, bytes):
                            data = data.decode('utf-8')
                        new_task = data
                        break
                    await asyncio.sleep(0.1)
                
                if new_task:
                    task = new_task
                    history.append({"role": "user", "content": task})
                    await session_manager.update_session(session_id, {"status": "running", "task": task})

        except Exception as e:
            print(f"DEBUG: Orchestrator failed with exception: {e}")
            logger.error("session_failed", session_id=session_id, error=str(e))
            await session_manager.update_session(session_id, {"status": "failed", "error": str(e)})
        finally:
            await context.close()

agent_orchestrator = AgentOrchestrator()
