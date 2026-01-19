import os
from langfuse import get_client
from app.core.settings import get_settings
from openinference.instrumentation.google_genai import GoogleGenAIInstrumentor

settings = get_settings()


os.environ["LANGFUSE_PUBLIC_KEY"] = settings.LANGFUSE_PUBLIC_KEY
os.environ["LANGFUSE_SECRET_KEY"] = settings.LANGFUSE_SECRET_KEY
os.environ["LANGFUSE_BASE_URL"] = settings.LANGFUSE_BASE_URL

GoogleGenAIInstrumentor().instrument()
langfuse = get_client()

assert langfuse.auth_check()
