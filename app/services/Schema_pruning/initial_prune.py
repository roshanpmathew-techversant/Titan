import re
from typing import Dict, Any
from app.models.schema import PrunedResponse, TableSchema, ForeignKey

# Regex to ignore system tables
SYSTEM_TABLE_PATTERN = re.compile(
    r"(log|logs|meta|fallback|session|role|auth|permission)",
    re.IGNORECASE,
)

# Types considered numeric
NUMERIC_TYPES = {
    "int", "integer", "bigint", "smallint",
    "decimal", "numeric", "float", "double", "real"
}

# Types considered time/datetime
TIME_TYPES = {
    "timestamp", "timestamp without time zone",
    "timestamp with time zone",
    "date", "datetime", "time"
}


def is_analytics(table_name: str, table_def: Dict[str, Any]) -> bool:
    """
    Determines if a table should be considered for analytics.
    - Must have at least one numeric column and one time column.
    - Excludes system tables matching SYSTEM_TABLE_PATTERN.
    """
    if SYSTEM_TABLE_PATTERN.search(table_name):
        return False

    has_numeric = False
    has_time = False

    columns = table_def.get("columns", {})
    for col_type in columns.values():
        if not isinstance(col_type, str):
            continue
        ct = col_type.lower().strip()
        if ct in NUMERIC_TYPES:
            has_numeric = True
        if ct in TIME_TYPES:
            has_time = True

    return has_numeric and has_time


def initial_prune(schema: Dict[str, Any]) -> PrunedResponse:
    """
    Prunes a schema dict to only include tables considered analytics tables.
    Wraps each table definition in TableSchema objects and returns a PrunedResponse.
    """
    pruned_tables: Dict[str, TableSchema] = {}
    tables = schema.get("tables", {})

    for table_name, table_def in tables.items():
        if is_analytics(table_name=table_name, table_def=table_def):
            pruned_tables[table_name] = TableSchema(
                columns=table_def.get("columns", {}),
                primary_key=table_def.get("primary_key", []),
                foreign_keys=table_def.get("foreign_keys", [])
            )

    # print(pruned_tables)

    return PrunedResponse(
        version='v2',
        tables=pruned_tables
    )
