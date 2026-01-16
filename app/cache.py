import redis
import json
import hashlib


redis_client = redis.Redis(host='localhost', port=6379, db=0)


def cache_key(db_id: str, schema_name: str) -> str:
    return f"schema:{db_id}:{schema_name}"

def get_cached_schema(key: str):
    val = redis_client.get(key)
    return json.loads(val) if val else None

def set_cached_schema(key: str, schema: dict):
    redis_client.set(key, json.dumps(schema), ex=3600)
