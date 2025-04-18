from fastapi import Depends, Query, Path
from typing import List, Optional

from api.controllers.astronomy_api.base_controller import BaseController
from api.services.body_service import BodyService
from api.schemas.body import BodyResponse, BodyListResponse

class BodiesController(BaseController):
    """
    Controller for celestial bodies endpoints using the Astronomy API.
    
    This controller handles requests related to celestial bodies,
    such as retrieving body information and listing available bodies.
    """
    
    def __init__(self):
        super().__init__(router_prefix="/astronomy/bodies", tags=["Astronomy Bodies"])
    
    def _register_routes(self) -> None:
        """Register all routes for the bodies controller"""
        
        @self.router.get("/{body_id}", response_model=BodyResponse)
        async def get_body(
            body_id: str = Path(..., description="ID of the celestial body"),
            force_refresh: bool = Query(False, description="Force refresh cached data"),
            latitude: float = Query(0.0, description="Observer latitude in degrees"),
            longitude: float = Query(0.0, description="Observer longitude in degrees"),
            elevation: float = Query(0.0, description="Observer elevation in meters"),
            body_service: BodyService = Depends()
        ):
            """
            Get information about a specific celestial body using Astronomy API.
            
            Retrieves detailed information about a celestial body, including its
            position, distance, and other properties. If data is cached and not
            expired, returns cached data. Otherwise, fetches fresh data from
            the astronomy API.
            """
            return await body_service.get_body(
                body_id=body_id,
                force_refresh=force_refresh,
                preferred_source="astronomy_api",
                latitude=latitude,
                longitude=longitude,
                elevation=elevation
            )
        
        @self.router.get("/multiple", response_model=List[BodyResponse])
        async def get_multiple_bodies(
            body_ids: str = Query(..., description="Comma-separated list of body IDs"),
            force_refresh: bool = Query(False, description="Force refresh cached data"),
            body_service: BodyService = Depends()
        ):
            """
            Get information about multiple celestial bodies using Astronomy API.
            
            Retrieves detailed information about multiple celestial bodies in a
            single request. This endpoint is more efficient than making multiple
            requests to the /bodies/{body_id} endpoint.
            
            Example: /astronomy/bodies/multiple?body_ids=mars,moon,jupiter
            """
            # Parse the comma-separated list of body IDs
            ids_list = [bid.strip() for bid in body_ids.split(",")]
            
            return await body_service.get_multiple_bodies(
                body_ids=ids_list,
                force_refresh=force_refresh,
                preferred_source="astronomy_api"
            )
        
        @self.router.get("", response_model=BodyListResponse)
        async def list_bodies(
            body_service: BodyService = Depends()
        ):
            """
            List all available celestial bodies from Astronomy API.
            
            Returns a list of all celestial bodies available from the astronomy API.
            """
            return await body_service.list_bodies(
                preferred_source="astronomy_api"
            )