from fastapi import FastAPI
from app.api.routes.schema import router as schema_router
from app.api.routes.user_req import router as user_req_router

app = FastAPI(title="Titan ChatBot", version="1.0")

app.include_router(schema_router)
app.include_router(user_req_router)