from fastapi import Depends, Query, Path
from typing import List, Optional

from api.controllers.nasa_api.base_controller import BaseController
from api.services.api.nasa_api_client import NasaApiClient
from api.schemas.body import BodyResponse, BodyListResponse

class BodiesController(BaseController):
    """
    Controller for NASA API celestial bodies endpoints.
    
    This controller handles requests related to celestial bodies from the NASA API,
    such as retrieving body information and listing available bodies.
    """
    
    def __init__(self):
        super().__init__(router_prefix="/nasa/bodies", tags=["NASA Bodies"])
    
    def _register_routes(self) -> None:
        """Register all routes for the NASA bodies controller"""
        
        @self.router.get("/{body_id}", response_model=BodyResponse)
        async def get_body(
            body_id: str = Path(..., description="ID of the celestial body"),
            force_refresh: bool = Query(False, description="Force refresh cached data"),
            latitude: float = Query(0.0, description="Observer latitude in degrees"),
            longitude: float = Query(0.0, description="Observer longitude in degrees"),
            elevation: float = Query(0.0, description="Observer elevation in meters"),
            nasa_client: NasaApiClient = Depends()
        ):
            """
            Get information about a specific celestial body from NASA API.
            
            Retrieves detailed information about a celestial body, including its
            position, distance, and other properties from the NASA API. If data is cached and not
            expired, returns cached data. Otherwise, fetches fresh data from
            the NASA API.
            """
            return await nasa_client.get_body(
                body_id=body_id,
                latitude=latitude,
                longitude=longitude,
                elevation=elevation
            )
        
        @self.router.get("/multiple", response_model=List[BodyResponse])
        async def get_multiple_bodies(
            body_ids: str = Query(..., description="Comma-separated list of body IDs"),
            force_refresh: bool = Query(False, description="Force refresh cached data"),
            nasa_client: NasaApiClient = Depends()
        ):
            """
            Get information about multiple celestial bodies from NASA API.
            
            Retrieves detailed information about multiple celestial bodies in a
            single request from the NASA API. This endpoint is more efficient than making multiple
            requests to the /nasa/bodies/{body_id} endpoint.
            
            Example: /nasa/bodies/multiple?body_ids=mars,moon,jupiter
            """
            # Parse the comma-separated list of body IDs
            ids_list = [bid.strip() for bid in body_ids.split(",")]
            
            # Get each body and collect results
            results = []
            for body_id in ids_list:
                body_data = await nasa_client.get_body(body_id=body_id)
                results.append(body_data)
            
            return results
        
        @self.router.get("", response_model=BodyListResponse)
        async def list_bodies(
            nasa_client: NasaApiClient = Depends()
        ):
            """
            List all available celestial bodies from NASA API.
            
            Returns a list of all celestial bodies available from the NASA API.
            """
            bodies = await nasa_client.list_bodies()
            return {"bodies": bodies}