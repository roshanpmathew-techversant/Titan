from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "Titan_chat"
    APP_VERSION: str = "1.0"

    REDIS_ENABLED: bool = False
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_TTL: int = 3600

    

    DB_TENANT_ANALYTICS: str
    DB_TENANT_ANALYTICS_SCHEMA: str
    DB_ID: str


    GEMINI_API_KEY: str | None = None

    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_BASE_URL: str | None = None

    class Config:
        env_file = ".env"

@lru_cache
def get_settings() -> Settings:
    return Settings()
