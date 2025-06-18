from fastapi import APIRouter
from .routes import router as report_router

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(
    report_router,
    prefix="/api/v1",
    tags=["medical-reports"]
)

# Export the router
__all__ = ["api_router"]