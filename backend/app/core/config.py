from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise Agentic RPA"
    VERSION: str = "1.0.0"
    
    # DATABASE
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "rpa_platform"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # WORKER
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # LLM
    LLM_PROVIDER: str = "openai" # openai, grok, azure, anthropic, mock
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = None # e.g. https://api.grok.x.ai/v1 or Azure endpoint
    LLM_MODEL: str = "gpt-4-turbo-preview" # or grok-1
    OPENAI_API_VERSION: Optional[str] = None # for Azure
    
    # Legacy specific keys (optional, but good for backward compat if needed)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # LOGGING
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
