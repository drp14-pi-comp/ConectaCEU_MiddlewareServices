"""Health check controller"""
from fastapi import APIRouter

from src.infrastructure.configuration.settings import config
from src.infrastructure.handlers.datetime_handler import DateTimeHandler

router = APIRouter(tags=["Health"])

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": config.settings.APP_NAME,
        "version": config.settings.APP_VERSION,
        "environment": config.settings.ENVIRONMENT,
        "timestamp": DateTimeHandler.now()
    }