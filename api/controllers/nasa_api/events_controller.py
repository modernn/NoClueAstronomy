from fastapi import Depends, Query, Path
from typing import Optional
from datetime import datetime, timedelta

from api.controllers.nasa_api.base_controller import BaseController
from api.services.api.nasa_api_client import NasaApiClient
from api.schemas.event import EventResponse

class EventsController(BaseController):
    """
    Controller for NASA API astronomical events endpoints.
    
    This controller handles requests related to astronomical events from the NASA API,
    such as retrieving events for a specific celestial body.
    """
    
    def __init__(self):
        super().__init__(router_prefix="/nasa/events", tags=["NASA Events"])
    
    def _register_routes(self) -> None:
        """Register all routes for the NASA events controller"""
        
        @self.router.get("/{body_id}", response_model=EventResponse)
        async def get_events(
            body_id: str = Path(..., description="ID of the celestial body"),
            start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format (default: current date)"),
            end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format (default: current date + 30 days)"),
            force_refresh: bool = Query(False, description="Force refresh cached data"),
            latitude: float = Query(0.0, description="Observer latitude in degrees"),
            longitude: float = Query(0.0, description="Observer longitude in degrees"),
            elevation: float = Query(0.0, description="Observer elevation in meters"),
            nasa_client: NasaApiClient = Depends()
        ):
            """
            Get astronomical events for a specific celestial body from NASA API.
            
            Retrieves astronomical events such as oppositions, conjunctions,
            and moon phases for a specific celestial body within a date range
            from the NASA API. If data is cached and not expired, returns cached data.
            Otherwise, fetches fresh data from the NASA API.
            """
            # Set default dates if not provided
            if not start_date:
                start_date = datetime.utcnow().strftime("%Y-%m-%d")
            
            if not end_date:
                end_date = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
            
            return await nasa_client.get_events(
                body_id=body_id,
                start_date=start_date,
                end_date=end_date,
                latitude=latitude,
                longitude=longitude,
                elevation=elevation
            )