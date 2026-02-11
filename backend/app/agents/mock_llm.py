import json
from typing import List, Dict
from app.agents.llm import LLMProvider

class MockLLMProvider(LLMProvider):
    async def generate(self, messages: List[Dict[str, str]], json_mode: bool = True) -> str:
        # The system prompt contains the history. It is usually the first message.
        system_prompt = messages[0]["content"] if len(messages) > 0 and messages[0]["role"] == "system" else ""
        
        if "Previous Steps:" in system_prompt:
            history_part = system_prompt.split("Previous Steps:")[1]
        else:
            history_part = ""
        
        # Simple heuristic to simulate an agent loop
        # Check history to see what created steps we have
        
        if 'open_url' not in history_part: 
            return json.dumps({
                "thought_summary": "I need to navigate to google.com first.",
                "action": "open_url",
                "args": {"url": "https://google.com"},
                "confidence": 1.0,
                "done": False
            })
        elif 'type_text' not in history_part:
             return json.dumps({
                "thought_summary": "I am on google, I will type the search query.",
                "action": "type_text",
                "args": {"selector": "textarea[name='q']", "text": "Agentic RPA"},
                "confidence": 1.0,
                "done": False
            })
        else:
            return json.dumps({
                "thought_summary": "I have typed the text, I am done for this test.",
                "action": "finish",
                "args": {"final_answer": "Searched for Agentic RPA"},
                "confidence": 1.0,
                "done": True
            })

# We can inject this in config or main if testing mode is enabled
