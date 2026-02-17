from app.core.secrets import get_gemini_api_key
from app.llm.gemini import gemini_llm_call
from langfuse import observe


@observe(name="response_formatter")
def format_response(user_req: str, db_response: dict) -> str:
    print("Formatter Called")
@observe(name="response_formatter")
def format_response(user_req: str, db_response: dict) -> str:
    """
    Formats raw DB results into a clean, user-friendly response
    using Gemini LLM.
    """    
    if not user_req:
        return "Invalid request."

    if not db_response:
        return "No records found."

    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError("Gemini API key is not configured.")
    
    

    system_prompt = """
    You are a response formatter.

    Your ONLY job is to convert raw database query results into a clear,
    concise, and user-friendly answer based strictly on the user's request.

    Rules:
    - Do NOT add new information.
    - Do NOT hallucinate or assume missing data.
    - If the result contains dates, return only a bullet list of dates.
    - If the result set is empty, clearly say no records were found.
    - Use clean formatting (bullet points, short paragraphs, or tables if needed).
    - Keep the answer concise and relevant.
    - Do NOT mention SQL, database, or system details.
    """

        # Always pass structured JSON
    user_prompt = f"""
    User Request:
    {user_req}

    Database Result:
    {db_response}

    Format the final answer now.
    """

    try:
        formatted_text = gemini_llm_call(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            api_key=api_key,
            metadata="response_formatter"
        )

        return formatted_text.strip()

    except Exception as e:
        print(f"[Response Formatter Error] {e}")
        return "Unable to format the response at this time."