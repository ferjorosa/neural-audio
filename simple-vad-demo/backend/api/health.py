"""Health check endpoints."""

from fastapi import APIRouter
from services.connection_service import ConnectionService

router = APIRouter()

# Shared connection service instance
connection_service = ConnectionService()


@router.get("/")
async def root():
    """Basic health check endpoint."""
    return {
        "message": "Simple VAD Demo Backend",
        "status": "running",
        "active_connections": connection_service.connection_count
    }


@router.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "active_connections": connection_service.connection_count,
        "vad_model": "silero-vad"
    }
