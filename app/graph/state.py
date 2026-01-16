from typing import TypedDict, Optional, Dict, Any
from app.models import SchemaResponse


class TitanState(TypedDict):
    user_query: str

    db_id: str

    schema_name: str

    schema: Optional[SchemaResponse]

    # intent: Optional[Dict[str, Any]]
    # pruned_schema: Optional[Dict[str, Any]]