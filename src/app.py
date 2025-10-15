from fastapi import FastAPI

# Ensure environment variables from .env are loaded at startup
# This import triggers load_dotenv() defined in src.config
import src.config  # noqa: F401

from src.api.endpoints import router

# Create FastAPI application
app = FastAPI()

# Include API router
app.include_router(router)