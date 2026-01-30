from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from app.services.openai_client import client

router = APIRouter()


class HealthResponse(BaseModel):
    status: str  # "healthy" | "degraded"
    timestamp: str
    service: str
    version: str
    openai_available: bool

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2026-01-29T12:34:56.789Z",
                "service": "AI Support Intelligence",
                "version": "1.0.0",
                "openai_available": True,
            }
        }


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check (API & OpenAI)",
    description="Returns the health status of the API and OpenAI connectivity. Status is 'healthy' if all systems are operational, or 'degraded' if OpenAI is unavailable.",
)
async def health_check():
    """
    Quick health check for API and OpenAI connectivity.
    
    Returns:
        HealthResponse: Service status with timestamp and OpenAI availability.
        
    Response (200 OK):
        {
            "status": "healthy",
            "timestamp": "2026-01-29T12:34:56.789Z",
            "service": "AI Support Intelligence",
            "version": "1.0.0",
            "openai_available": true
        }
    """
    openai_available = False
    
    # Check OpenAI API availability
    try:
        # Make a lightweight API call to verify connectivity
        client.models.list()
        openai_available = True
    except Exception:
        openai_available = False
    
    return HealthResponse(
        status="healthy" if openai_available else "degraded",
        timestamp=datetime.utcnow().isoformat() + "Z",
        service="AI Support Intelligence",
        version="1.0.0",
        openai_available=openai_available,
    )
