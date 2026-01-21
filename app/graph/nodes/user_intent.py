from app.core.secrets import get_gemini_api_key
from app.llm.gemini import gemini_llm_call
from app.graph.state import TitanState, IntentResult
import json
import re
from langfuse import get_client
from langfuse import observe
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor



DEFAULT_INTENT: IntentResult = {
    "intent_type": "SOCIAL",
    "business_entities": [],
    "metrics": [],
    "dimensions": [],
    "time_range": None,
    "filters": [],
    "confidence": 0.8
}
@observe()
def intent_extractor_node(state: TitanState) -> TitanState:
    """
    Extract the Intent of the user query using Gemini API and update the TitanState.
    Fully instrumented with Langfuse observability.
    """

    if state is None:
        state = {}

    user_query = state.get("user_query", "").strip()
    if not user_query:
        return state

    system_prompt = """
    You are an analytics intent extraction engine.
    Extract the user's intent as JSON only using this schema:
    {
        "intent_type": "AGGREGATE | LIST | FILTER | COMPARE | TREND | SUMMARY | SOCIAL"
        "business_entities": [],
        "metrics": [],
        "dimensions": [],
        "time_range": None,
        "filters": [],
        "confidence": 0-1
    }
    Do not add explanations or extra text.
    """
    user_prompt = f'User Query:\n"{user_query}"\nReturn the JSON intent.'

    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError("Gemini API key is not configured.")

    try:
        response_text = gemini_llm_call(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            api_key=api_key,
            metadata={
                "node": "intent_extractor_node",
            }
        )

        response_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", response_text, flags=re.IGNORECASE).strip()

        if response_text:
            try:
                intent = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"[intent_extractor_node] Failed to parse JSON: {e}")
                print(f"[intent_extractor_node] Response was: {response_text}")
                intent = DEFAULT_INTENT.copy()
        else:
            intent = DEFAULT_INTENT.copy()

        for key, default_value in DEFAULT_INTENT.items():
            if key not in intent:
                intent[key] = default_value

    except Exception as e:
        print(f"[intent_extractor_node] Gemini failed: {e}")
        intent = DEFAULT_INTENT.copy()

    return {
        **state,
        "intent": intent
    }
