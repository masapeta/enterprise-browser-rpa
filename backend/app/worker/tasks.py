import asyncio
from celery import shared_task
from app.agents.orchestrator import agent_orchestrator
from app.core.logger import logger

@shared_task(bind=True, name="app.worker.run_agent_task")
def run_agent_task(self, session_id: str, task_description: str):
    logger.info("worker_received_task", session_id=session_id)
    
    # Run async function in sync Celery worker
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    loop.run_until_complete(agent_orchestrator.run_session(session_id, task_description))
    
    return {"status": "completed", "session_id": session_id}
