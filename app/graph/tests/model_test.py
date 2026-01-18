import google.generativeai as genai
from app.core.secrets import get_gemini_api_key

genai.configure(api_key=get_gemini_api_key())

models = list(genai.list_models())
print(models.name)

