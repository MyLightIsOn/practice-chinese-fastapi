from fastapi import FastAPI

from src.api.endpoints import router

# Create FastAPI application
app = FastAPI()

# Include API router
app.include_router(router)