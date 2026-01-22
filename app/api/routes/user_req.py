from fastapi import APIRouter, HTTPException
from app.graph.graph import build_titan_graph
from app.models.user import UserRequest, UserResponse
from app.graph.state import TitanState
from app.services.write_to_file import write_pruned_table_names

router = APIRouter()
graph = build_titan_graph()

@router.post("/user_request", response_model=UserResponse)
def user_input(req: UserRequest):
    """
    Handle user requests and return a response including the extracted intent
    """

    state: TitanState = {
        "user_query": req.user_req,
    }

    try:
        result = graph.invoke(state)

        # fallback intent
        intent = result.get("intent")
        if not intent:
            intent = {
                "intent_type": "SUMMARY",
                "business_entities": [],
                "metrics": [],
                "dimensions": [],
                "time_range": None,
                "filters": [],
                "confidence": 0.8,
            }

        # pruned_schema is already a PrunedResponse object
        pruned_schema = result.get("pruned_schema")
        write_pruned_table_names(pruned_schema, "llm_pruned_schema.txt")

        # Optional: if you need dict access
        # pruned_schema_dict = pruned_schema.model_dump()

    except Exception as e:
        print(f"Error processing user request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "success",
        "message": intent,
        "pruned_schema": pruned_schema  # ✅ leave as PrunedResponse
    }
