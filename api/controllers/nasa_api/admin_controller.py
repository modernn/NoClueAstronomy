from fastapi import Depends, Query
from datetime import datetime

from api.controllers.nasa_api.base_controller import BaseController
from api.services.api.nasa_api_client import NasaApiClient
from api.schemas.admin import HealthResponse, ApiInfo

class AdminController(BaseController):
    """
    Controller for NASA API administration endpoints.
    
    This controller handles requests related to NASA API administration,
    such as health checks and API information.
    """
    
    def __init__(self):
        super().__init__(router_prefix="/nasa", tags=["NASA Administration"])
    
    def _register_routes(self) -> None:
        """Register all routes for the NASA admin controller"""
        
        @self.router.get("/health", response_model=HealthResponse)
        async def health_check(
            nasa_client: NasaApiClient = Depends()
        ):
            """
            Check the health of the NASA API.
            
            Checks the health of the NASA API connection. Returns a status of "ok"
            if the API is healthy, or "error" if it's not.
            """
            # Check the NASA API health
            is_healthy = await nasa_client.check_health()
            
            # Determine the overall status
            status = "ok" if is_healthy else "error"
            
            return HealthResponse(
                status=status,
                database="ok",  # Database is always assumed to be OK here
                apis={"nasa_api": is_healthy},
                time=datetime.utcnow(),
                version="1.0.0"  # You might want to import this from config
            )
        
        @self.router.get("/", response_model=ApiInfo)
        async def get_api_info():
            """
            Get NASA API information.
            
            Returns basic information about the NASA API integration,
            such as its name, description, and version.
            """
            return ApiInfo(
                name="NASA Astronomy API",
                description="NASA API integration for the NoClueAstronomy API",
                version="1.0.0",  # You might want to import this from config
                documentation="/docs",
                status="/nasa/health"
            )