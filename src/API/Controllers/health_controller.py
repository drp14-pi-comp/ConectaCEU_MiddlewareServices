"""Health check controller"""
from fastapi import APIRouter
from datetime import datetime

from src.infrastructure.configuration.settings import config

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": config.settings.APP_NAME,
        "version": config.settings.APP_VERSION,
        "environment": config.settings.ENVIRONMENT,
        "timestamp": datetime.utc(datetime.timezone.utc).isoformat()
    }