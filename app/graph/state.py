from typing import TypedDict, Optional, Dict, List
from app.models.schema import SchemaResponse, PrunedResponse

class IntentResult(TypedDict, total=False):
    intent_type: str                 # AGGREGATE | LIST | FILTER | COMPARE | TREND | SOCIAL
    keywords: List[str]
    business_entities: List[str]
    metrics: List[str]
    dimensions: List[str]
    time_range: Optional[str]
    filters: List[Dict[str, str]]
    confidence: float


class SqlValidationResult(TypedDict):
    is_valid: bool
    errors: List[str]

class TitanState(TypedDict, total=False):
    
    user_id: str
    chat_id: str
    
    user_query: str

    

    db_id: str

    schema_name: str

    sql_query: str

    response: str

    memory_hit: Optional[bool]

    schema: Optional[SchemaResponse]

    intent: Optional[IntentResult]

    response: Optional[str]

    # intent: Optional[Dict[str, Any]]
    pruned_schema: Optional[PrunedResponse]

    sql_validation: Optional[SqlValidationResult]
    #sql :



