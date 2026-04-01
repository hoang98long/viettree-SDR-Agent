# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Autonomous B2B Sales SDR Agent"
    OPENAI_API_KEY: str
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/sales_db"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    class Config:
        env_file = ".env"

settings = Settings()