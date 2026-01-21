from app.graph.state import TitanState
from app.services.Schema_pruning import initial_prune


def schema_pruner_node(state: TitanState) -> TitanState:
    raw_schema = state['schema']

    pruned_schema = initial_prune(raw_schema)

    return {
        **state,
        "pruned_schema": pruned_schema.model_dump()
    }