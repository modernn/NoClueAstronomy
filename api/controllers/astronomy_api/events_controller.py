from fastapi import Depends, Query, Path
from typing import Optional

from api.controllers.astronomy_api.base_controller import BaseController
from api.services.event_service import EventService
from api.schemas.event import EventResponse

class EventsController(BaseController):
    """
    Controller for astronomical events endpoints using Astronomy API.
    
    This controller handles requests related to astronomical events,
    such as retrieving events for a specific celestial body.
    """
    
    def __init__(self):
        super().__init__(router_prefix="/astronomy/events", tags=["Astronomy Events"])
    
    def _register_routes(self) -> None:
        """Register all routes for the events controller"""
        
        @self.router.get("/{body_id}", response_model=EventResponse)
        async def get_events(
            body_id: str = Path(..., description="ID of the celestial body"),
            start_date: Optional[str] = Query(None, description="Start date in YYYY-MM-DD format (default: current date)"),
            end_date: Optional[str] = Query(None, description="End date in YYYY-MM-DD format (default: current date + 30 days)"),
            force_refresh: bool = Query(False, description="Force refresh cached data"),
            latitude: float = Query(0.0, description="Observer latitude in degrees"),
            longitude: float = Query(0.0, description="Observer longitude in degrees"),
            elevation: float = Query(0.0, description="Observer elevation in meters"),
            event_service: EventService = Depends()
        ):
            """
            Get astronomical events for a specific celestial body using Astronomy API.
            
            Retrieves astronomical events such as oppositions, conjunctions,
            and moon phases for a specific celestial body within a date range.
            If data is cached and not expired, returns cached data. Otherwise,
            fetches fresh data from the astronomy API.
            """
            return await event_service.get_events(
                body_id=body_id,
                start_date=start_date,
                end_date=end_date,
                force_refresh=force_refresh,
                preferred_source="astronomy_api",
                latitude=latitude,
                longitude=longitude,
                elevation=elevation
            )