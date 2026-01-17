from fastapi import FastAPI
from app.api.routes.schema import router as schema_router

app = FastAPI(title="Titan ChatBot", version="1.0")

app.include_router(schema_router)