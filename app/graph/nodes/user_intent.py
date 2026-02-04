from app.core.secrets import get_gemini_api_key
from app.llm.gemini import gemini_llm_call
from app.graph.state import TitanState, IntentResult
import json
import re
from langfuse import get_client
from langfuse import observe
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

call_llm = True

DEFAULT_INTENT: IntentResult = {
    "intent_type": "SOCIAL",
    "keywords": [],
    "business_entities": [],
    "metrics": [],
    "dimensions": [],
    "time_range": None,
    "filters": [],
    "confidence": 0.8
}

@observe()
def intent_extractor_node(state: TitanState) -> TitanState:
    if state is None:
        state = {}

    user_query = state.get("user_query", "").strip()
    if not user_query:
        return state

    response_text = None  

    if call_llm:
        api_key = get_gemini_api_key()
        if not api_key:
            raise RuntimeError("Gemini API key is not configured.")

        system_prompt = """
    You are a STRICT analytics intent extraction engine.

    Your job is to EXTRACT ONLY what the user has EXPLICITLY stated.
    DO NOT infer, assume, or add business logic.

    Rules:
    - Use AGGREGATE if the user asks for totals, counts, averages, summaries, OR "highest/lowest" (ranking).
    - Use COMPARE only if the user explicitly compares two or more entities or categories.
    - Use TREND only if the user explicitly asks for change over time.
    - Use SOCIAL if user communicates in a social way like hi,hello,thank you or other social greetings
    - Otherwise, intent_type MUST be LIST.

    Time & Date Rules:
    - Capture BOTH dimensions and ranges. 
    - Dimensions: If "daily", "monthly", etc., are mentioned, add "day" or "month" to 'dimensions'.
    - Time Range: If a period is mentioned—absolute ("Jan 2025") or relative ("this quarter", "last month", "yesterday")—extract it into 'time_range'. 

    Filter & Value Rules:
    - Filters must be expressed as (field, operator, value).
    - VALUE DETECTION: If you detect specific names, categories, or labels (e.g., 'birthday', 'XAH', 'anniversary') that are not metrics, extract them as filters.
    - Sorting: "highest/lowest" is a ranking intent; do NOT create a filter for these terms.

    Keyword Extraction Rules:
- Extract SINGLE-WORD keywords verbatim from the request and convert to lowercase.
- KEYWORD EXPANSION: For every extracted keyword, you MUST also include any "Priority" keywords that are logically related to the domain context, even if not explicitly in the request.
- RELATIONSHIP MAPPING (Internal Logic):
    * If 'products' or 'outlet' -> add 'sales', 'store', 'transaction'
    * If 'customer' or 'member' -> add 'sales', 'orders', 'cohort, data'
    * If 'performance' or 'analytics' -> add 'report', 'summary', 'metrics'
    * If 'campaign' or 'marketing' -> add 'cohort', 'performance'
- ALL keywords must be chosen strictly from the Priority List.
- Keywords MUST be lowercase.
    {
      "intent_type": "LIST | AGGREGATE | COMPARE | TREND | FILTER | SOCIAL",
      "keywords": [],
      "business_entities": [],
      "metrics": [],
      "dimensions": [],
      "time_range": null, // String or Object. Example: "this quarter" or "2025-01-01 to 2025-01-31"
      "filters": [{"field": "string", "operator": "=", "value": "string"}],
      "confidence": 0.0-1.0
    }
"""



        user_prompt = f'User Query:\n"{user_query}"\nReturn the JSON intent.'

        response_text = gemini_llm_call(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            api_key=api_key,
            metadata={"node": "intent_extractor_node"},
        )

        response_text = re.sub(
            r"^```(?:json)?\s*|\s*```$", "",
            response_text,
            flags=re.IGNORECASE,
        ).strip()

    if response_text:
        try:
            intent = json.loads(response_text)
        except json.JSONDecodeError:
            intent = DEFAULT_INTENT.copy()
    else:
        intent = DEFAULT_INTENT.copy()

    for key, default_value in DEFAULT_INTENT.items():
        intent.setdefault(key, default_value)

        

    return {
        **state,
        "intent": intent,
    }
