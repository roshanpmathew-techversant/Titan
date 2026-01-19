from google import genai
from app.core.secrets import get_gemini_api_key
from app.llm.langfuse import langfuse  # single client

def gemini_llm_call(system_prompt, user_prompt, api_key=None, metadata=None):
    if api_key is None:
        api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    client = genai.Client(api_key=api_key)
    full_prompt = f"{system_prompt}\n{user_prompt}"

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=full_prompt,
    )

    if metadata:
        langfuse.update_current_trace(
            input=full_prompt,
            output=response.text,
            metadata=metadata
        )

    return response.text.strip()
