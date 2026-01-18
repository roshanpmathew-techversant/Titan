# app/core/settings.py
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "Titan_chat"
    APP_VERSION: str = "1.0"

    REDIS_ENABLED: bool 
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_CACHE_TTL: int = 3600

    DEFAULT_SCHEMA: str = "public"

    DB_TENANT_ANALYTICS: str 

    GEMINI_API_KEY: str | None = None

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
