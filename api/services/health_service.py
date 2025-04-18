import logging
from datetime import datetime
from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import get_db
from app.services.api_gateway_service import ApiGatewayService
from app.config import API_VERSION

# Configure logging
logger = logging.getLogger(__name__)

class HealthService:
    """
    Service for checking API health.
    
    This service provides methods for checking the health of
    the API and its dependencies.
    """
    
    def __init__(
        self, 
        db: Session = Depends(get_db),
        api_gateway: ApiGatewayService = Depends()
    ):
        self.db = db
        self.api_gateway = api_gateway
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check the health of the API and its dependencies.
        
        Returns:
            Dictionary containing health status information
        """
        health_status = {
            "status": "ok",
            "database": "ok",
            "apis": {},
            "time": datetime.utcnow(),
            "version": API_VERSION
        }
        
        # Check database connection
        try:
            # Simple query to check DB connection
            self.db.execute("SELECT 1").fetchall()
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            health_status["database"] = "error"
            health_status["status"] = "error"
        
        # Check external APIs
        api_health = await self.api_gateway.check_health()
        health_status["apis"] = api_health
        
        # If any API is unhealthy, mark the overall status as degraded
        if not all(api_health.values()):
            if health_status["status"] == "ok":
                health_status["status"] = "degraded"
        
        return health_status
    
    def get_api_info(self) -> Dict[str, str]:
        """
        Get basic API information.
        
        Returns:
            Dictionary containing API information
        """
        return {
            "name": "NoClueAstronomy API",
            "description": "An API that queries and caches astronomical data from various sources",
            "version": API_VERSION,
            "documentation": "/docs",
            "status": "/health"
        }