from app.graph.state import TitanState
from typing import  List

def sql_validator(state: TitanState ) -> TitanState:
    errors: List[str] = []
    normalized_sql = state.strip().lower()

    # Block non-SELECT queries
    if not normalized_sql.startswith("select"):
        errors.append("Only SELECT queries are allowed")

    # Block dangerous keywords
    forbidden_keywords = ["insert", "update", "delete", "drop", "alter"]
    for keyword in forbidden_keywords:
        if re.search(rf"\\b{keyword}\\b", normalized_sql):
            errors.append(f"Forbidden keyword detected: {keyword}")

    # Block SELECT *
    if re.search(r"select\\s+\\*", normalized_sql):
        errors.append("SELECT * is not allowed")


    # Enforce LIMIT
    if "limit" not in normalized_sql:
        errors.append("LIMIT clause is required")


    # Extract tables
    table_matches = re.findall(r"from\\s+(\\w+)", normalized_sql)
    for table in table_matches:
        if table not in pruned_schema:
            errors.append(f"Table not allowed: {table}")


    # Extract columns
    select_match = re.search(r"select\\s+(.*?)\\s+from", normalized_sql)
    if select_match:
        columns = [c.strip() for c in select_match.group(1).split(",")]
        for col in columns:
            if "." in col:
                table, column = col.split(".", 1)
                if (table not in pruned_schema or column not in pruned_schema[table]):
                    errors.append(f"Invalid column reference: {col}")
            else:
                if not any(col in cols for cols in pruned_schema.values()):
                    errors.append(f"Unknown column: {col}")

    return{
        **state,
        "is_valid":len(errors) == 0,
        "errors":errors
    }