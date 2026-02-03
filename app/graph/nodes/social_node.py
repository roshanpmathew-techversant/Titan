from app.graph.state import TitanState
from langfuse import observe

@observe(name="social_node")
def social_node(state: TitanState) -> TitanState:
    """
    Stops the pipeline for SOCIAL intent and returns a short response.
    """

    intent = state.get("intent", {})
    confidence = intent.get("confidence", 0.0)

    # Very short & safe replies only
    response = "Hi! I can help you with analytics questions. Ask me about data, reports, or trends."

    return {
        **state,
        "final_response": response,
        "stop_pipeline": True,
        "social_confidence": confidence,
    }
