from langgraph.graph import StateGraph , END
from app.graph.state import TitanState

from app.graph.nodes.user_input import user_input_node
from app.graph.nodes.social_node import social_node
from app.graph.nodes.schema_loader import schema_loader_node
from app.graph.nodes.user_intent import intent_extractor_node
from app.graph.nodes.schema_pruner import schema_pruner_node
from app.graph.nodes.sql_generator import sql_generator_node
from app.graph.nodes.sql_validator import sql_validator
from app.graph.nodes.response_generator import response_generator_node

def route_after_intent(state: TitanState) -> str:
    """
    Conditional routing after intent extraction
    """
    intent = state.get("intent", {})
    if intent.get("intent_type") == "SOCIAL":
        return "social_node"
    return "schema_loader"


def build_titan_graph():
    graph = StateGraph(TitanState)
    graph.add_node("user_input", user_input_node)
    graph.add_node("schema_loader", schema_loader_node)
    graph.add_node("intent_extractor", intent_extractor_node) 
    graph.add_node("social_node", social_node)       
    graph.add_node("schema_pruner", schema_pruner_node)
    graph.add_node("sql_generator", sql_generator_node)
    graph.add_node("sql_validator", sql_validator)
    graph.add_node("response_generator", response_generator_node)




    graph.set_entry_point("user_input")
    graph.add_edge("user_input", "intent_extractor")
    graph.add_conditional_edges(
        "intent_extractor",
        route_after_intent,
        {
            "social_node": "social_node",
            "schema_loader": "schema_loader",
        },
    )
    graph.add_edge("social_node", END)

    # graph.add_edge("intent_extractor", "schema_loader")
    graph.add_edge("schema_loader", "schema_pruner")
    graph.add_edge("schema_pruner", "sql_generator")
    graph.add_edge("sql_generator", "sql_validator")
    graph.add_edge("sql_validator", "response_generator")
    graph.add_edge("response_generator", END)

    return graph.compile()