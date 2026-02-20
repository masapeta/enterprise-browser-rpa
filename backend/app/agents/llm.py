from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.core.config import settings

class LLMProvider:
    async def generate(self, messages: List[Dict[str, str]], json_mode: bool = True) -> str:
        raise NotImplementedError

class OpenAICompatibleProvider(LLMProvider):
    """Handles OpenAI, Groq, and other compatible APIs"""
    def __init__(self):
        msg = f"Initializing OpenAICompatibleProvider with base_url={settings.LLM_BASE_URL}, model={settings.LLM_MODEL}"
        print(msg)
        
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY or settings.OPENAI_API_KEY,
            base_url=settings.LLM_BASE_URL # Required for Groq
        )
        self.model = settings.LLM_MODEL or "gpt-4-turbo-preview"

    async def generate(self, messages: List[Dict[str, str]], json_mode: bool = True) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0
        }
        if json_mode:
            # Note: Grok beta might not support strict json_object mode yet, 
            # but usually OpenAI compat APIs do.
            # If Grok fails with this, we might need a flag to disable it.
            kwargs["response_format"] = {"type": "json_object"}
            
        try:
            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            raise e

class AzureOpenAIProvider(LLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            api_version=settings.OPENAI_API_VERSION,
            azure_endpoint=settings.LLM_BASE_URL,
        )
        self.deployment_name = settings.LLM_MODEL

    async def generate(self, messages: List[Dict[str, str]], json_mode: bool = True) -> str:
        kwargs = {
            "model": self.deployment_name, # Azure uses deployment name as model
            "messages": messages,
            "temperature": 0.0
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        response = await self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

import os
from app.agents.mock_llm import MockLLMProvider

from groq import AsyncGroq

class GroqProvider(LLMProvider):
    def __init__(self):
        self.client = AsyncGroq(
            api_key=settings.LLM_API_KEY,
        )
        self.model = settings.LLM_MODEL or "openai/gpt-oss-120b"

    async def generate(self, messages: List[Dict[str, str]], json_mode: bool = True) -> str:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.0
        }
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
            
        try:
            response = await self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq Generation Error: {e}")
            raise e

def get_llm_provider():
    provider_type = settings.LLM_PROVIDER.lower()
    
    if os.getenv("USE_MOCK_LLM") == "true" or provider_type == "mock":
        return MockLLMProvider()
    
    if provider_type == "azure":
        return AzureOpenAIProvider()
    
    if provider_type == "groq":
        return GroqProvider()
    
    # Default covers "openai" and generic compatible APIs
    return OpenAICompatibleProvider()

llm_service = get_llm_provider()
