from google import genai
from app.core.secrets import get_gemini_api_key

client = genai.Client(api_key=get_gemini_api_key())

models = list(client.models.list())

for m in models:
    print(m.name)