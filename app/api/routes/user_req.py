from fastapi import APIRouter, HTTPException
from app.graph.graph import build_titan_graph
from app.models.user import UserRequest, UserResponse
from app.models.schema import PrunedResponse
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

        intent = result.get("intent")
        if not intent:
            intent = {
                "intent_type": "SOCIAL",
                "keywords": [],
                "business_entities": [],
                "metrics": [],
                "dimensions": [],
                "time_range": None,
                "filters": [],
                "confidence": 0.8,
            }

        pruned_schema = result.get("pruned_schema")
        if not pruned_schema or not isinstance(pruned_schema, PrunedResponse):
            pruned_schema = PrunedResponse(
            version="v2",
            tables={}
        )
        write_pruned_table_names(pruned_schema, "llm_pruned_schema.txt")

        

        sql_query = result.get("sql_query")
        validation = result.get("sql_validation")
        response = result.get("response")
        

    except Exception as e:
        print(f"Error processing user request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "success",
        "message": intent,
        "pruned_schema": pruned_schema,
        "sql_query": sql_query,
        "sql_validation": validation,
        "response": response
    }
