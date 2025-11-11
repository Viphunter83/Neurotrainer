"""
Health check endpoint.

Simple endpoint to verify the API is running.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status information about the API
    """
    return {
        "status": "healthy",
        "service": "FitnessAI Backend",
        "version": "0.1.0",
    }

