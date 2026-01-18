from fastapi import APIRouter, HTTPException
from app.graph.graph import build_titan_graph
from app.models.user import UserRequest, UserResponse
from app.graph.state import TitanState


router = APIRouter()


graph = build_titan_graph()

@router.post("/user_request", response_model=UserResponse)
def user_input(req: UserRequest):
    """
    Handle user requests and return a response including the extracted intent

    """

    state: TitanState = {
        'user_query': req.user_req,
        
    }

    try:
        result = graph.invoke(state)

        intent = result.get("intent", {})

        if not intent:
            intent = {"intent_type": "SUMMARY"}



    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    return {
        "status": "success",
        "message": intent
    }