from app.graph.state import TitanState
from app.loader import load_schema  # reuse existing logic


def schema_loader_node(state: TitanState) -> TitanState:
    schema = load_schema(
        db_id=state["db_id"],
        schema_name=state["schema_name"]
    )

    return {
        **state,
        "schema": schema
    }
