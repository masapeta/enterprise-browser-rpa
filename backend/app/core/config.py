from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise Agentic RPA"
    VERSION: str = "1.0.0"
    
    # DATABASE
    MONGODB_URL: str = "mongodb://localhost:27017" # Mongo handles localhost better on Windows usually
    MONGODB_DB_NAME: str = "rpa_platform"
    REDIS_URL: str = "redis://127.0.0.1:6379/0" 
    
    # WORKER
    CELERY_BROKER_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://127.0.0.1:6379/0"
    
    # LLM
    LLM_PROVIDER: str = "groq" # openai, groq, azure, anthropic, mock
    LLM_API_KEY: Optional[str] = None
    LLM_BASE_URL: Optional[str] = "https://api.groq.com/openai/v1" 
    LLM_MODEL: str = "llama3-70b-8192" 
    OPENAI_API_VERSION: Optional[str] = None # for Azure
    
    # Legacy specific keys (optional, but good for backward compat if needed)
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # LOGGING
    LOG_LEVEL: str = "INFO"
    
    # BROWSER
    HEADLESS: bool = True # Set to False for local dev/interactive mode

    class Config:
        env_file = ".env"

settings = Settings()
