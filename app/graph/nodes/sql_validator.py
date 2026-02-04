from typing import List
from app.graph.state import TitanState
import sqlglot
from sqlglot import exp


FORBIDDEN_STATEMENTS = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Alter,
    exp.Drop,
    exp.Create,
)


def sql_validator(state: TitanState) -> TitanState:
    errors: List[str] = []

    sql = state.get("sql_query")

    if not sql or not isinstance(sql, str):
        return {
            **state,
            "sql_query": "invalid",
            "sql_validation": {
                "is_valid": False,
                "errors": ["SQL query is missing or invalid"],
            },
        }

    try:
        expression = sqlglot.parse_one(sql)
    except sqlglot.errors.ParseError as e:
        return {
            **state,
            "sql_query": "invalid",
            "sql_validation": {
                "is_valid": False,
                "errors": [f"SQL parse error: {str(e)}"],
            },
        }

    if not isinstance(expression, exp.Select):
        errors.append("Only SELECT queries are allowed")

    for forbidden in FORBIDDEN_STATEMENTS:
        if expression.find(forbidden):
            errors.append("DB mutating statements are not allowed")
            break

    for proj in expression.expressions:
        if isinstance(proj, exp.Star):
            errors.append("SELECT * is not allowed")

    is_valid = len(errors) == 0

    return {
        **state,
        "sql_query": state["sql_query"] if is_valid else "invalid",
        "sql_validation": {
            "is_valid": is_valid,
            "errors": errors,
        },
    }
