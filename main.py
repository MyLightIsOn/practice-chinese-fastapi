"""
Main entry point for the FastAPI application.
"""

from src.app import app

# This allows the app to be run directly with `python main.py`
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)