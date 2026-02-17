from google import genai
from app.core.secrets import get_gemini_api_key

client = genai.Client(api_key=get_gemini_api_key())

text_to_embed = "User prefers dark mode and works night shifts."


response = client.models.embed_content(
    model="models/gemini-embedding-001",
    contents=text_to_embed
)

embedding = response.embeddings[0].values