from fastapi import FastAPI , HTTPException
import psycopg2

from app.models import SchemaRequest, SchemaResponse
from app.loader import load_schema
from app.cache import cache_key, get_cached_schema, set_cached_schema
from app.secrets import get_connection_string


app = FastAPI(title="Schema Service", version="1.0")

@app.post("/schema/load", response_model=SchemaResponse)
def load(req: SchemaRequest):
    conn_str = get_connection_string(req.db_id)

    if not conn_str:
        raise HTTPException(status_code=404, detail = "Db ID is  Unknown")
    
    key = cache_key(req.db_id, req.schema_name)
    cached = get_cached_schema(key)

    if cached:
        return cached
    

    try:
        conn = psycopg2.connect(conn_str)
    except:
        raise HTTPException(status_code=400, detail="DB connection failed")
    

    schema = load_schema(conn, req.schema_name)

    conn.close()

    res = {
        "version": "v1",
        "tables": schema["tables"]
    }

    set_cached_schema(key, res)

    return res