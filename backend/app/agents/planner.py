import json
from typing import List, Dict, Any
from app.agents.llm import llm_service
from app.core.logger import logger

PLANNER_PROMPT = """
You are an autonomous browser agent. Your goal is to complete the user's task: "{task}"

You must output a JSON object with the following structure:
{{
    "thought_summary": "Short reasoning about the current state and what to do next",
    "action": "Name of the tool to execute (open_url, click, type_text, get_page_text, finish)",
    "args": {{ ... arguments for the tool ... }},
    "confidence": 0.9,
    "done": false
}}

If the task is complete, set "action" to "finish", "done" to true, and put your final answer in "args": {{ "final_answer": "..." }}.

Available Tools:
- open_url(url: str)
- click(selector: str)
- type_text(selector: str, text: str)
- get_page_text()
- get_screenshot()

Current Browser Context:
{context}

Previous Steps:
{history}
"""

class Planner:
    async def plan(self, task: str, history: List[Dict], context: str) -> Dict[str, Any]:
        try:
            messages = [
                {"role": "system", "content": PLANNER_PROMPT.format(task=task, history=json.dumps(history[-5:]), context=context)},
                {"role": "user", "content": "What is the next step?"}
            ]
        
            response_text = await llm_service.generate(messages, json_mode=True)
            plan = json.loads(response_text)
            return plan
        except Exception as e:
            logger.error("planning_failed", error=str(e))
            # Fallback or retry logic could go here
            return {"thought_summary": "Error in planning", "action": "wait", "args": {}, "done": False}

planner = Planner()
