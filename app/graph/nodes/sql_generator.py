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
Generate ONE valid SQL SELECT query, No \n .
JUST THE SQL QUERY

STRICT RULES:
- Output ONLY SQL.
- No explanations.
- No markdown.
- Use ONLY tables and columns provided in the schema.
- DO NOT invent tables or columns.
- Only SELECT queries allowed.
- ALWAYS include LIMIT.
- AGGREGATE without dimensions is valid.
- Use GROUP BY ONLY when dimensions are provided.
- No subqueries.
- No CTEs.
- No UPDATE, DELETE, INSERT.
- Use JOINs ONLY if joins are explicitly provided in the schema.

SUPPORTED INTENTS:
- AGGREGATE (SUM, COUNT, AVG)
- LIST (SELECT / SELECT DISTINCT)
- FILTER (WHERE)
- COMPARE (GROUP BY dimensions)
- TREND (GROUP BY time dimension, ORDER BY time)

COMBINED TABLE RESOLUTION RULES:
- You may ONLY use physical table names provided in logical_to_physical.
- You must NEVER invent table names.
- Logical tables in pruned_schema must be resolved to physical tables using logical_to_physical.
- If a filter uniquely identifies a single physical table (e.g., store code = XAH), select only that table.
- If no filter uniquely identifies a physical table, generate a UNION ALL over all relevant physical tables.
- NEVER reference logical table names in the final SQL.
- If multiple physical tables are used, they MUST have identical schemas.

FAILURE RULE:
If SQL cannot be generated safely, output exactly:
SELECT 'INVALID_QUERY';
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

    if not intent or intent.get("intent_type") not in {"AGGREGATE", "LIST", "FILTER"}:
        return {
            **state,
            "sql_query": "SELECT 'INVALID_QUERY';"
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

    return {
        **state,
        "sql_query": sql
    }
