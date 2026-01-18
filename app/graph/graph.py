from langgraph.graph import StateGraph , END
from app.graph.state import TitanState

from app.graph.nodes.user_input import user_input_node
from app.graph.nodes.schema_loader import schema_loader_node
from app.graph.nodes.user_intent import intent_extractor_node


def build_titan_graph():
    graph = StateGraph(TitanState)
    graph.add_node("user_input", user_input_node)
    graph.add_node("schema_loader", schema_loader_node)
    graph.add_node("intent_extractor", intent_extractor_node)

    graph.set_entry_point("user_input")
    graph.add_edge("user_input", "intent_extractor")
    graph.add_edge("intent_extractor", "schema_loader")
    graph.add_edge("schema_loader", END)
    return graph.compile()