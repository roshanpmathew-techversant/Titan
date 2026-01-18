import os
from app.core.settings import get_settings

def get_connection_string(db_id: str) -> str | None:
    """
    Resolve DB connection string in this order:
    1️⃣ OS environment variable (DB_<DB_ID>)
    2️⃣ Pydantic Settings fallback
    """
    env_key = f"DB_{db_id.upper()}"

    value = os.getenv(env_key)
    if value:
        print(f"Using OS ENV for {env_key}")
        return value

    settings = get_settings()
    value = getattr(settings, env_key, None)
    if value:
        print(f"Using Settings fallback for {env_key}")
        return value

    print(f"No connection string found for {env_key}")
    return None

def get_gemini_api_key() -> str:
    settings = get_settings()
    api_key = settings.GEMINI_API_KEY

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Please configure it in environment or .env"
        )

    return api_key
