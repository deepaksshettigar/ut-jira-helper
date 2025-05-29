"""
Script to run the FastAPI application.
Can be executed with: poetry run python run.py
"""
import uvicorn

def main():
    """Run the FastAPI application."""
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    main()