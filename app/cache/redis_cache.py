import redis, json
from functools import lru_cache
from redis.exceptions import ConnectionError, TimeoutError
from app.core.settings import get_settings

settings = get_settings()

@lru_cache
def get_redis_client():
    return redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1,
    )

def cache_key(db_id: str, schema_name: str) -> str:
    return f"schema:{db_id}:{schema_name}"

def get_cached_schema(key: str):
    try:
        client = get_redis_client()
        val = client.get(key)
        return json.loads(val) if val else None
    except (ConnectionError, TimeoutError, json.JSONDecodeError):
        return None

def set_cached_schema(key: str, schema: dict, ttl: int | None = None):
    try:
        client = get_redis_client()
        client.setex(
            key,
            ttl or settings.REDIS_CACHE_TTL,
            json.dumps(schema)
        )
    except (ConnectionError, TimeoutError):
        pass
