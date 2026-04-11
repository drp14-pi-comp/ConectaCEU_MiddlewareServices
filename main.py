"""Main FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.infrastructure.configuration.settings import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    print(f"🚀 Starting {config.settings.APP_NAME} v{config.settings.APP_VERSION}")
    print(f"📌 Environment: {config.settings.ENVIRONMENT}")
    print(f"🗄️  Database: {config.settings.DATABASE_NAME} on {config.settings.DATABASE_HOST}")
    
    # Initialize database connection pool
    # db_manager.initialize()  # We'll uncomment this after creating database module
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    # db_manager.dispose_engine()

def create_app() -> FastAPI:
    """Application factory pattern"""
    app = FastAPI(
        title=config.settings.APP_NAME,
        version=config.settings.APP_VERSION,
        description="FastAPI application with MySQL following .NET architecture",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/health", tags=["Health"])
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "app": config.settings.APP_NAME,
            "version": config.settings.APP_VERSION,
            "environment": config.settings.ENVIRONMENT
        }
    
    # Root endpoint
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint"""
        return {
            "message": f"Welcome to {config.settings.APP_NAME}",
            "docs": "/api/docs",
            "health": "/health"
        }
    
    return app

# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
