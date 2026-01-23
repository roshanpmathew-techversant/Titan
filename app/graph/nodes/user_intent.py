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

    response_text = None  # 🔑 IMPORTANT

    if call_llm:
        api_key = get_gemini_api_key()
        if not api_key:
            raise RuntimeError("Gemini API key is not configured.")

        system_prompt = """
                You are a STRICT analytics intent extraction engine.

        Your job is to EXTRACT ONLY what the user has EXPLICITLY stated.
        DO NOT infer, assume, normalize, or add business logic.

        Rules:
        - Use AGGREGATE only if the user explicitly asks for totals, counts, averages, or summaries.
        - Use COMPARE only if the user explicitly compares two or more entities or categories.
        - Use TREND only if the user explicitly asks for change over time.
        - Otherwise, intent_type MUST be LIST.
        - Only include business_entities, metrics, dimensions, filters, and keywords if they are explicitly mentioned.
        - If a time interval such as daily, monthly, quarterly, or yearly is mentioned, include the corresponding time dimension (day, month, quarter, year).
        - Filters must be expressed as structured conditions when possible (field, operator, value). Do NOT invent filters.
        - If unsure about any field, leave it empty.
        - Confidence must be less than 1.0 unless the request is fully explicit and unambiguous.

        Keyword extraction rules:
        Extract ONLY important, domain-relevant SINGLE-WORD keywords from the user request.

        Keywords MUST appear verbatim (case-insensitive) in the user request.

        Do NOT combine words into phrases.

        Do NOT normalize, expand, or infer synonyms.

        Keywords MUST be lowercase.

        Prefer concrete business nouns over verbs or adjectives.

        Time expressions must be reduced to a single atomic token (e.g., "day", "month", "quarter", "year") if explicitly mentioned.

        Country, region, product, campaign, or entity names are allowed ONLY if explicitly stated.

        Keep the list minimal and precise (typically 5–7 keywords).

        Priority: Always try to select keywords from the provided allowed list first. Only use other words if no suitable match exists in the list.
        Allowed keywords (pick the most relevant ones from this list):

        sales, transaction, orders, store, retail, outlet, customer, member, delivery, product, category, region, location, campaign, cohort, marketing, report, analytics, performance, ticket, issue, feedback, day, month, quarter, year, system, rating, log, activity, migration, meta, schema, user, session, role, master, test, summary, temp, chatbot, chat, prediction, scoring
        
        Allowed intent_type values:
        - LIST
        - AGGREGATE
        - COMPARE
        - TREND
        - SOCIAL

        Return ONLY valid JSON matching this schema:
        {
        "intent_type": "LIST | AGGREGATE | COMPARE | TREND | SOCIAL",
        "keywords": [],
        "business_entities": [],
        "metrics": [],
        "dimensions": [],
        "time_range": null,
        "filters": [],
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
