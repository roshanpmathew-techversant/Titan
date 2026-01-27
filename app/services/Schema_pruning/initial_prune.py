import re
from typing import Dict, Any, List
from app.models.schema import PrunedResponse, TableSchema
from app.graph.state import IntentResult

# Types considered numeric
NUMERIC_TYPES = {
    "int", "integer", "bigint", "smallint",
    "decimal", "numeric", "float", "double", "real"
}

# Types considered time/datetime
TIME_TYPES = {
    "timestamp",
    "timestamp without time zone",
    "timestamp with time zone",
    "date",
    "datetime",
    "time"
}


def build_keyword_pattern(keywords: List[str]) -> re.Pattern | None:
    """
    Builds a regex pattern from intent keywords.
    Returns None if no keywords are provided.
    """
    if not keywords:
        return None

    escaped = [re.escape(k) for k in keywords]
    return re.compile(rf"({'|'.join(escaped)})", re.IGNORECASE)


def is_analytics(
    table_name: str,
    table_def: Dict[str, Any],
    keyword_pattern: re.Pattern | None
) -> bool:
    """
    A table is analytics-relevant ONLY if:
    - Table name matches at least one intent keyword
    - Has at least one numeric column
    - Has at least one time/datetime column
    """

    # 1. Keyword gate (mandatory)
    if keyword_pattern and not keyword_pattern.search(table_name):
        return False

    has_numeric = True
    has_time = True

    columns = table_def.get("columns", {})
    for col_type in columns.values():
        if not isinstance(col_type, str):
            continue

        ct = col_type.lower().strip()
        if ct in NUMERIC_TYPES:
            has_numeric = True
        if ct in TIME_TYPES:
            has_time = True

        # Early exit optimization
        if has_numeric and has_time:
            return True

    return False


def initial_prune(schema: Dict[str, Any], intent: IntentResult) -> PrunedResponse:
    """
    Prunes schema to only include analytics-relevant tables
    based strictly on intent keywords + column types.
    """

    keywords = intent.get("keywords", [])
    keyword_pattern = build_keyword_pattern(keywords)
    print(keyword_pattern)

    pruned_tables: Dict[str, TableSchema] = {}
    tables = schema.get("tables", {})
    

    for table_name, table_def in tables.items():
        if is_analytics(
            table_name=table_name,
            table_def=table_def,
            keyword_pattern=keyword_pattern
        ):
            pruned_tables[table_name] = TableSchema(
                columns=table_def.get("columns", {}),
                primary_key=table_def.get("primary_key", []),
                foreign_keys=table_def.get("foreign_keys", [])
            )

    return PrunedResponse(
        version="v2",
        tables=pruned_tables
    )
