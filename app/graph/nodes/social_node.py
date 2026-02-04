from app.graph.state import TitanState

from langfuse import observe

import json
import re
from app.core.settings import get_settings
from app.llm.gemini import gemini_llm_call

from app.core.secrets import get_gemini_api_key
 

settings = get_settings()
 
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
        print('API KEY error')    
        return {**state, "response": "Okay 👍"}
    
    social_prompt = settings.SOCIAL_PROMPT
 
    system_prompt = social_prompt.strip()
    # print(system_prompt)
 
    user_prompt = f"User message:\n{user_query}"
 
    try:
        raw_response = gemini_llm_call(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            api_key=api_key,
            metadata={"node": "social_node"},
        )

        # print("Social Node: Raw Res-> ", raw_response)

        
        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            raw_response.strip(),
            flags=re.IGNORECASE,
        )

        # print("Social Node: Cleaned Res-> ", cleaned)

        parsed = json.loads(cleaned)
        # print("Social Node: Parsed Res-> ", parsed)

        reply = parsed.get("response", "").strip()
        # print("Social Node: Reply Res-> ", reply)

        if not reply:                    
            print('Parsing Error')    

            reply = "Okay 👍"

    except Exception as e:
        print("Social Node Error:", e)
        reply = "Okay 👍"

    
    return {

        **state,

        "response": reply

    }

 