from fastapi import FastAPI
from app.api.v1.api import api_router
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine, SessionLocal
from app.init.init_db import populate_initial_data

app = FastAPI(
    title="FastAPI Ecommerce API",
    description="FastAPI Ecommerce Project",
    version="0.1.0",
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set the domains that can access the API,
    allow_credentials=True,
    allow_methods=["*"],  # Set the HTTP methods that are allowed
    allow_headers=["*"],  # Set the HTTP headers that are allowed
)

# Create all tables
Base.metadata.create_all(bind=engine)


# Initialize the database with some data
# @app.on_event("startup")
# async def startup_event():
#     try:
#         with SessionLocal() as db:
#             populate_initial_data(db)
#     except Exception as e:
#         print(f"Error initializing database: {e}")


# Include API routes
app.include_router(api_router)


# Root route
@app.get("/")
async def root():
    return {"message": "Hello, Welcome to use FastAPI Ecommerce API!"}
