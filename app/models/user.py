from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.models.schema import PrunedResponse
from app.graph.state import SqlValidationResult


class UserRequest(BaseModel):
    user_id: str
    chat_id: str
    user_req: str

class UserResponse(BaseModel):
    status: str
    intent: Dict[str, Any]
    pruned_schema: Optional[PrunedResponse]
    sql_query: Optional[str]
    sql_validation: Optional[SqlValidationResult]
    response: Optional[str]
    