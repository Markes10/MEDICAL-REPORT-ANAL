from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from api.routes import router
from utils.helpers import format_json_output
from utils import logger, config

# Initialize FastAPI application with config values
app = FastAPI(
    title=config['app']['name'],
    description="AI-powered medical report analysis system",
    version=config['app']['version']
)

# Configure CORS using config values
app.add_middleware(
    CORSMiddleware,
    allow_origins=config['security']['cors_origins'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(
    router,
    prefix="/api/v1",
    tags=["medical-reports"]
)

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return format_json_output({
        "success": False,
        "error": str(exc.detail),
        "status_code": exc.status_code
    })

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}")
    return format_json_output({
        "success": False,
        "error": "Internal server error",
        "status_code": 500
    })

# Health check endpoint
@app.get("/health")
async def health_check():
    return format_json_output({
        "status": "healthy",
        "version": app.version
    })

# Application startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {config['app']['name']} API")
    # Initialization code can go here

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {config['app']['name']} API")
    # Cleanup code can go here

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config['app']['host'],
        port=config['app']['port'],
        reload=config['app']['debug']
    )

# Post-run project guidance
print("✅ Missing files created!")
print("\nTo complete your project:")
print("1. Replace your requirements.txt with the fixed version")
print("2. Add the missing files shown above")
print("3. Create missing __init__.py files in all directories")
print("4. Install dependencies: pip install -r requirements.txt")
print("5. Install Tesseract OCR on your system")
print("6. Run: python main.py")
