from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./hirebot.db"
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""  # ADD THIS LINE
    CLAUDE_MODEL: str = "claude-3-sonnet-20240229"
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
