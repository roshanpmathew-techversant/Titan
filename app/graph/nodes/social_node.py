from app.graph.state import TitanState

from langfuse import observe

import json

from app.llm.gemini import gemini_llm_call

from app.core.secrets import get_gemini_api_key
 
 
STATIC_REPLIES = {

    "hi": "Hey 👋",

    "hello": "Hello!",

    "thanks": "You’re welcome 🙂",

    "thank you": "Happy to help!",

}
 
 
@observe

def social_node(state: TitanState) -> TitanState:

    user_query = state.get("user_query", "").strip()
 
    if not user_query:

        return {**state, "response": "Okay 👍"}
 
    normalized = user_query.lower().strip()
 
    if normalized in STATIC_REPLIES:

        return {

            **state,

            "response": STATIC_REPLIES[normalized]

        }
 
    

    api_key = get_gemini_api_key()

    if not api_key:

        return {**state, "response": "Okay 👍"}
 
    system_prompt = """

    You are Titan’s Social Response Node.
    
    You will be called ONLY when the user message is already classified as SOCIAL.
    
    Your job is to produce a short, friendly reply.
    
    Rules:

    - 1 sentence only

    - No questions

    - No explanations

    - No system or data references
    
    Respond in JSON only:

    {

    "response": "<friendly social reply>"

    }

    """.strip()
 
    user_prompt = f"User message:\n{user_query}"
 
    try:

        raw_response = gemini_llm_call(

            system_prompt=system_prompt,

            user_prompt=user_prompt,

            api_key=api_key,

            metadata={"node": "social_node"},

        )
 
        parsed = json.loads(raw_response)

        reply = parsed.get("response", "").strip()
 
        if not reply:

            reply = "Okay 👍"
 
    except Exception:

        reply = "Okay 👍"
 
    return {

        **state,

        "response": reply

    }

 