from fastapi import APIRouter, HTTPException
from app.graph.graph import build_titan_graph
from app.models.schema import SchemaResponse, SchemaRequest, PrunedResponse
from app.graph.nodes.schema_loader import schema_loader_node

router = APIRouter()

graph = build_titan_graph()


@router.post("/load_schema", response_model=SchemaResponse)
def load_schema(req: SchemaRequest):
    """Load and return the schema of the Titan graph database."""
    try:
        result = schema_loader_node({
            "db_id": req.db_id,
            "schema_name": req.schema_name
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail= str(e))
    
    return{
        "version": "v1",
        "tables": result["schema"]["tables"]
    }