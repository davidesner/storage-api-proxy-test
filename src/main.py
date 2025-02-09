from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from storage_api_proxy.api.endpoints import router
from storage_api_proxy.core.config import get_settings
from storage_api_proxy.core.logging import setup_logging
from storage_api_proxy.services.database import WorkspaceDatabase

# Setup logging
setup_logging()

# Create FastAPI application
app = FastAPI(
    title="Storage API Proxy",
    description="A proxy service for executing SQL queries in Keboola Storage API workspaces",
    version="1.0.0"
)

# Create database instance
db = WorkspaceDatabase()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.on_event("startup")
async def startup_event():
    """Initialize application resources on startup."""
    settings = get_settings()
    
    # Initialize database
    await db.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup application resources on shutdown."""
    await db.close() 