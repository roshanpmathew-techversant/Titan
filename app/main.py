from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.routes.schema import router as schema_router
from app.api.routes.user_req import router as user_req_router
from app.db.memory_db import initialize_memory_schema


@asynccontextmanager
async def lifespan(app: FastAPI):
    
    initialize_memory_schema()
    print("Memory schema initialized ✅")

    yield

    
    print("App shutting down...")


app = FastAPI(
    title="Titan ChatBot",
    version="1.0",
    lifespan=lifespan
)

app.include_router(schema_router)
app.include_router(user_req_router)