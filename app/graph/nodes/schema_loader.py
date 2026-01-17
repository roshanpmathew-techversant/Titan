import psycopg2
from app.db.schema_loader import load_schema
from app.core.secrets import get_connection_string
from app.graph.state import TitanState
from app.cache.redis_cache import cache_key, get_cached_schema, set_cached_schema

def schema_loader_node(state: TitanState) -> TitanState:
    """
        Load the database schema based on user query and db_id
    """

    key = cache_key(state["db_id"], state["schema_name"])
    cached = get_cached_schema(key)

    if cached: 
        return {**state, "schema": cached}
    
    conn_str = get_connection_string(state['db_id'])

    if not conn_str:
        raise ValueError(f"No connection string found for db_id: {state['db_id']}")
    
    conn = psycopg2.connect(conn_str)

    try:
        schema = load_schema(conn=conn, schema_name=state["schema_name"])
    finally:
        conn.close()

    set_cached_schema(key, schema)

    return {
        **state,
        "schema": schema
    }