from langgraph.graph import StateGraph , END
from app.graph.state import TitanState

from app.graph.nodes.user_input import user_input_node
from app.graph.nodes.schema_loader import schema_loader_node
from app.graph.nodes.user_intent import intent_extractor_node
from app.graph.nodes.schema_pruner import schema_pruner_node
from app.graph.nodes.sql_generator import sql_generator_node

def build_titan_graph():
    graph = StateGraph(TitanState)
    graph.add_node("user_input", user_input_node)
    graph.add_node("schema_loader", schema_loader_node)
    graph.add_node("intent_extractor", intent_extractor_node)        
    graph.add_node("schema_pruner", schema_pruner_node)
    graph.add_node("sql_generator", sql_generator_node)



    graph.set_entry_point("user_input")
    graph.add_edge("user_input", "intent_extractor")
    graph.add_edge("intent_extractor", "schema_loader")
    graph.add_edge("schema_loader", "schema_pruner")
    graph.add_edge("schema_pruner", "sql_generator")
    graph.add_edge("sql_generator", END)
    return graph.compile()