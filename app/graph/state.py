from typing import TypedDict, Optional, Dict, List
from app.models.schema import SchemaResponse, PrunedResponse

class IntentResult(TypedDict, total=False):
    intent_type: str                 # AGGREGATE | LIST | FILTER | COMPARE | TREND | SUMMARY
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
    user_query: str

    db_id: str

    schema_name: str

    schema: Optional[SchemaResponse]

    intent: Optional[IntentResult]

    # intent: Optional[Dict[str, Any]]
    pruned_schema: Optional[PrunedResponse]

    sql_validator: Optional[SqlValidationResult]
    #sql :



