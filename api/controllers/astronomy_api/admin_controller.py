from fastapi import Depends, Query
from typing import Optional

from api.controllers.astronomy_api.base_controller import BaseController
from api.services.cache_service import CacheService
from api.services.health_service import HealthService
from api.schemas.admin import CacheStats, CacheClearResponse, HealthResponse, ApiInfo

class AdminController(BaseController):
    """
    Controller for administration endpoints related to Astronomy API.
    
    This controller handles requests related to administration,
    such as cache management and health checks.
    """
    
    def __init__(self):
        super().__init__(router_prefix="/astronomy", tags=["Astronomy Administration"])
    
    def _register_routes(self) -> None:
        """Register all routes for the admin controller"""
        
        @self.router.get("/cache/stats", response_model=CacheStats)
        async def get_cache_stats(
            cache_service: CacheService = Depends()
        ):
            """
            Get statistics about the Astronomy API cache.
            
            Retrieves statistics about the cache, such as the number of bodies
            cached, the number of events cached, and when the oldest cached
            data was created.
            """
            return cache_service.get_cache_stats()
        
        @self.router.delete("/cache/clear", response_model=CacheClearResponse)
        async def clear_cache(
            clear_search_history: bool = Query(False, description="Whether to also clear search history"),
            cache_service: CacheService = Depends()
        ):
            """
            Clear all cached Astronomy API data.
            
            Deletes all cached data, including bodies and events. Optionally
            also clears search history if clear_search_history is true.
            """
            return cache_service.clear_cache(clear_search_history=clear_search_history)
        
        @self.router.get("/health", response_model=HealthResponse)
        async def health_check(
            health_service: HealthService = Depends()
        ):
            """
            Check the health of the Astronomy API connection.
            
            Checks the health of the API and its dependencies, such as the
            database and external Astronomy API. Returns a status of "ok" if everything
            is healthy, "degraded" if some components are unhealthy, or "error"
            if critical components are unhealthy.
            """
            return await health_service.check_health()
        
        @self.router.get("/", response_model=ApiInfo)
        async def get_api_info(
            health_service: HealthService = Depends()
        ):
            """
            Get Astronomy API information.
            
            Returns basic information about the Astronomy API integration,
            such as its name, description, and version.
            """
            return health_service.get_api_info()