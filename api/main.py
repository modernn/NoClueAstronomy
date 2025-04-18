from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from api.config import (
    API_TITLE, 
    API_DESCRIPTION, 
    API_VERSION, 
    API_DOCS_URL, 
    API_REDOC_URL,
    CORS_ORIGINS,
    CORS_METHODS,
    CORS_HEADERS,
    RATE_LIMIT,
    RATE_LIMIT_WINDOW,
    RATE_LIMIT_BLOCK_TIME
)
from api.controllers import create_router
from api.middleware import RateLimiter
from api.models import init_db

# Configure logging
logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        Configured FastAPI application
    """
    # Create FastAPI app
    app = FastAPI(
        title=API_TITLE,
        description=API_DESCRIPTION,
        version=API_VERSION,
        docs_url=API_DOCS_URL,
        redoc_url=API_REDOC_URL,
    )
    
    # Add CORS middleware
    api.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=CORS_METHODS,
        allow_headers=CORS_HEADERS,
    )
    
    # Add rate limiting middleware
    api.add_middleware(
        RateLimiter,
        rate_limit=RATE_LIMIT,
        window_size=RATE_LIMIT_WINDOW,
        block_time=RATE_LIMIT_BLOCK_TIME,
    )
    
    # Register routes
    api.include_router(create_router())
    
    # Initialize database
    @api.on_event("startup")
    async def startup_event():
        logger.info("Initializing application...")
        init_db()
        logger.info("Application initialized successfully")
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)