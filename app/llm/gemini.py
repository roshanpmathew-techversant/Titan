from app.core.secrets import get_gemini_api_key
import google.generativeai as genai


from app.core.secrets import get_gemini_api_key
import google.generativeai as genai

def gemini_llm_call(system_prompt: str, user_prompt: str, api_key=None) -> str:
    """
    Call Gemini LLM to get response
    """

    if api_key is None:
        api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # Combine system + user prompt
    full_prompt = f"{system_prompt}\n{user_prompt}"
    response = model.generate_content(full_prompt)  # REMOVE temperature argument

    return response.text
