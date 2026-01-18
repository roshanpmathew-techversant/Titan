from pydantic import BaseModel
from typing import Dict, Any

class UserRequest(BaseModel):
    user_id: str
    user_req: str

class UserResponse(BaseModel):
    status: str
    message: Dict[str, Any]