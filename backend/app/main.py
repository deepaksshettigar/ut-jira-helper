import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

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
from app.api.conversation import router as conversation_router

# Include routers
app.include_router(tasks_router, prefix="/api")
app.include_router(conversation_router, prefix="/api")

# Mount React build directory as static files if it exists
build_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'frontend', 'build')
if os.path.exists(build_dir):
    app.mount("/", StaticFiles(directory=build_dir, html=True), name="static")

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