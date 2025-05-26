from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="UT Jira Helper API",
    description="API for the UT Jira Helper application",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import routers
from app.api.tasks import router as tasks_router

# Include routers
app.include_router(tasks_router, prefix="/api")

@app.get("/")
async def read_root():
    """
    Root endpoint returning API information.
    """
    return {
        "message": "Welcome to UT Jira Helper API",
        "version": "0.1.0",
        "docs": "/docs",
    }