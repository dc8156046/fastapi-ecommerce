from fastapi import FastAPI
from app.api.v1.api import api_router

app = FastAPI(title="FastAPI Demo", description="FastAPI Demo Project", version="0.1.0")

app.include_router(api_router)
