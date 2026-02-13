from app.core.secrets import get_connection_string
import psycopg2
from app.services.response_formater import format_response
from app.graph.state import TitanState
from app.core.settings import get_settings

settings = get_settings()


def response_generator_node(state: TitanState) -> TitanState:
    """
    Executes the generated SQL query and returns:
    - Formatted response (if successful)
    - Exact raw PostgreSQL error string (if execution fails)
    """

    if not state:
        return {"response": "Invalid state provided."}
    sql_query = state.get("sql_query")
    user_req = state.get("user_query")

    if not sql_query:
        return {**state, "response": "SQL query not found."}

    db_id = settings.DB_ID

    if not db_id:
        return {**state, "response": "Database configuration missing."}

    conn_str = get_connection_string(db_id)
    if not conn_str:
        return {**state, "response": f"No connection string found for db_id: {db_id}"}

    if "INVALID" in sql_query.upper():
        return {
            **state,
            "response": "SQL query is marked as INVALID. Execution skipped."
        }

    try:
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query)

                rows = cur.fetchall()

                if not rows:
                    return {
                        **state,
                        "response": "No records found."
                    }

                columns = [desc[0] for desc in cur.description]
                db_response = [dict(zip(columns, row)) for row in rows]
                # print(db_response)

    except psycopg2.Error as e:
        return {
            **state,
            "response": e.pgerror.strip() if e.pgerror else str(e)
        }

   
    except Exception as e:
        return {
            **state,
            "response": str(e)
        }

    formatted_response = format_response(user_req, db_response)

    return {
        **state,
        "response": formatted_response
    }