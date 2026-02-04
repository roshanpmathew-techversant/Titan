import json
from typing import Dict, Any, List
from app.graph.state import TitanState
from app.llm.gemini import gemini_llm_call
from app.core.secrets import get_gemini_api_key
from langfuse import observe
import re



def build_sql_system_prompt() -> str:
    """
    System prompt: ALL rules and behavior live here.
    """
    return """
    You are a SQL query generator.

    TASK:
    Generate ONE valid SQL SELECT query. 
    JUST THE SQL QUERY.

    STRICT RULES:
    - Output ONLY SQL.
    - No explanations.
    - No markdown.
    - Use ONLY tables and columns provided in the schema.
    - DO NOT invent tables or columns.
    - Only SELECT queries allowed.
    - ALWAYS include LIMIT (default 10).
    - No UPDATE, DELETE, INSERT.
    - Use JOINs ONLY if joins are explicitly provided in the schema.
    - CAST timestamps to DATE (e.g., column::date) when grouping by day/date to avoid granularity errors.
    - If a user's metric (e.g., 'potential') does not exist verbatim, use the most closely related numerical metric (e.g., 'revenue') provided in the schema.

    FIELD RESOLUTION RULES:
    - If a filter field is 'UNKNOWN', scan the text/string columns in the provided schema for the most logical match. 
    - (e.g., if value is 'birthday', and schema has 'cohort', map the filter to 'cohort').
    - If dimensions are missing from the intent but required for a metric (like 'highest'), include the most relevant category/identity column in the SELECT and GROUP BY.

    SUBQUERY & CTE RULES:
    - NO CTEs (Common Table Expressions).
    - NO Subqueries, EXCEPT when aggregating over a UNION ALL (see Combined Table Rules).

    SUPPORTED INTENTS:
    - AGGREGATE (SUM, COUNT, AVG) -> Must result in a single summary or grouped summary.
    - LIST (SELECT / SELECT DISTINCT)
    - FILTER (WHERE)
    - COMPARE (GROUP BY dimensions)
    - TREND (GROUP BY time dimension, ORDER BY time)

    COMBINED TABLE RESOLUTION RULES:
    - You may ONLY use physical table names provided in logical_to_physical.
    - Logical tables in pruned_schema must be resolved to physical tables using logical_to_physical.
    - If a filter uniquely identifies a single physical table (e.g., store code = XAH), select only that table.
    - If multiple physical tables are required (no unique filter):
    1. For LIST intents: Generate a UNION ALL of all relevant tables.
    2. For AGGREGATE intents: You MUST wrap the UNION ALL in a subquery. 
        (e.g., SELECT sum(x) FROM (SELECT x FROM table1 UNION ALL SELECT x FROM table2) AS all_data)
    - NEVER reference logical table names in the final SQL.
    - If multiple physical tables are used, they MUST have identical schemas.

    FAILURE RULE:
    If SQL cannot be generated safely, output exactly:
    SELECT 'INVALID_QUERY';
    Reason: along with the reason why SQL can't be generated in not more than 3 sentences.
    """.strip()


def build_sql_user_prompt(
    user_question: str,
    intent: Dict[str, Any],
    pruned_schema: Dict[str, Any],
    combined_tables: Dict[str, List[str]],
) -> str:
    """
    User prompt: INPUTS ONLY. No rules.
    """
    return f"""
USER_QUESTION:
{user_question}

INTENT:
{intent}

SCHEMA:
{pruned_schema}

COMBINED_TABLES:
{combined_tables}
""".strip()

@observe()
def sql_generator_node(state: TitanState) -> TitanState:
    intent = state.get("intent")

    pruned_schema = state.get('pruned_schema')
    pruned_schema = pruned_schema.tables
    user_question = state.get("user_query")
    combined_tables = state["schema"]["logical_to_physical"]

    # TEMP fallback until schema pruning is finalized
    if not pruned_schema:
        pruned_schema = {
            "fact_table": "transactionsdata",
            "metrics": {
                "sales": {
                    "column": "amount",
                    "aggregation": "SUM"
                }
            },
            "columns": {
                "transactionsdata": ["amount", "transaction_date", "store_id"]
            },
            "joins": [],
            "limit": 100
        }

    if not intent or intent.get("intent_type") not in {"AGGREGATE", "LIST", "FILTER","COMPARE","TREND","SUMMARY"}:
        return {
            **state,
            "sql_query": "INVALID_QUERY",
            "response": "Query Generation Failed"
        }

    system_prompt = build_sql_system_prompt()

    user_prompt = build_sql_user_prompt(
        user_question=user_question,
        intent=intent,
        pruned_schema=pruned_schema,
        combined_tables=combined_tables,
    )
    api_key = get_gemini_api_key()

    sql = gemini_llm_call(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        api_key=api_key,
        metadata={"node": "sql_generator"}
    )
    
    sql = re.sub(r"```sql|```", "", sql).strip()
    sql = " ".join(sql.split())
    inavlid = False

    if "INVALID" in sql:
        inavlid = True

    return {
        **state,
        "sql_query": sql,
        "response": "Query Generation Failed" if inavlid else "Query Generated"
    }
