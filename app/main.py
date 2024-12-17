from fastapi import FastAPI
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="FastAPI Ecommerce", description="FastAPI Ecommerce Project", version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set the domains that can access the API,
    allow_credentials=True,
    allow_methods=["*"],  # Set the HTTP methods that are allowed
    allow_headers=["*"],  # Set the HTTP headers that are allowed
)

app.include_router(api_router)
