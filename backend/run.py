"""
Script to run the FastAPI application.
Can be executed with: poetry run python run.py
"""
import uvicorn
import logging
import os

def main():
    """Run the FastAPI application."""
    # Set up logging
    log_level = os.getenv("APP_LOG_LEVEL", "info").upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()