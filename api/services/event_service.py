import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.models import get_db, CachedEvent
from api.schemas.event import EventResponse
from api.services.api_gateway_service import ApiGatewayService
from api.config import CACHE_EXPIRATION_HOURS

# Configure logging
logger = logging.getLogger(__name__)

class EventService:
    """
    Service for handling astronomical event data.
    
    This service provides methods for retrieving and caching
    astronomical events for celestial bodies.
    """
    
    def __init__(
        self,
        db: Session = Depends(get_db),
        api_gateway: ApiGatewayService = Depends()
    ):
        self.db = db
        self.api_gateway = api_gateway
    
    async def get_events(
        self,
        body_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        force_refresh: bool = False,
        preferred_source: Optional[str] = None,
        latitude: float = 0.0,
        longitude: float = 0.0,
        elevation: float = 0.0
    ) -> EventResponse:
        """
        Get events for a specific celestial body.
        
        Args:
            body_id: ID of the celestial body
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            force_refresh: Whether to force refresh cached data
            preferred_source: Preferred data source
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees
            elevation: Observer elevation in meters
            
        Returns:
            Events for the celestial body
        """
        # Get the current date
        now = datetime.utcnow()
        
        # Set default dates if not provided
        if not start_date:
            start_date = now.strftime("%Y-%m-%d")
        
        if not end_date:
            end_date = (now + timedelta(days=30)).strftime("%Y-%m-%d")
        
        # Create a cache key
        cache_key = f"{body_id}_{start_date}_{end_date}_{latitude}_{longitude}_{elevation}_{preferred_source or 'default'}"
        
        # Check cache if not forcing refresh
        if not force_refresh:
            cached_event = self._get_cached_event(cache_key)
            if cached_event:
                logger.info(f"Retrieved events for {body_id} from cache")
                return cached_event
        
        # Fetch fresh data
        try:
            logger.info(f"Fetching fresh events for {body_id}")
            event_data = await self.api_gateway.get_events(
                body_id=body_id,
                start_date=start_date,
                end_date=end_date,
                preferred_source=preferred_source,
                latitude=latitude,
                longitude=longitude,
                elevation=elevation
            )
            
            # Cache the result
            self._cache_event(
                cache_key=cache_key,
                body_id=body_id,
                start_date=start_date,
                end_date=end_date,
                event_data=event_data,
                preferred_source=preferred_source or "astronomy_api"
            )
            
            # Create response
            return EventResponse(
                body_id=body_id,
                events=event_data["events"],
                cached=False,
                last_updated=datetime.utcnow(),
                source=preferred_source or "astronomy_api"
            )
        except Exception as e:
            logger.error(f"Error fetching events for {body_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error fetching event data: {str(e)}"
            )
    
    def _get_cached_event(self, cache_key: str) -> Optional[EventResponse]:
        """
        Get a cached event if it exists and is not expired.
        
        Args:
            cache_key: Cache key for the event
            
        Returns:
            Cached event or None if not found or expired
        """
        # Find the cached event in the database
        cached = self.db.query(CachedEvent).filter(CachedEvent.id == cache_key).first()
        
        if not cached:
            return None
        
        # Check if the cache is expired
        expiration_time = cached.last_updated + timedelta(hours=CACHE_EXPIRATION_HOURS)
        if datetime.utcnow() > expiration_time:
            return None
        
        # Return the cached event
        return EventResponse(
            body_id=cached.body_id,
            events=cached.data["events"],
            cached=True,
            last_updated=cached.last_updated,
            source=cached.source
        )
    
    def _cache_event(
        self,
        cache_key: str,
        body_id: str,
        start_date: str,
        end_date: str,
        event_data: Dict[str, Any],
        preferred_source: str
    ) -> None:
        """
        Cache event data in the database.
        
        Args:
            cache_key: Cache key for the event
            body_id: ID of the celestial body
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            event_data: Event data to cache
            preferred_source: Data source
        """
        try:
            # Check if the event is already cached
            cached = self.db.query(CachedEvent).filter(CachedEvent.id == cache_key).first()
            
            if cached:
                # Update existing cache
                cached.data = event_data
                cached.last_updated = datetime.utcnow()
                cached.source = preferred_source
            else:
                # Create new cache entry
                cached = CachedEvent(
                    id=cache_key,
                    body_id=body_id,
                    start_date=start_date,
                    end_date=end_date,
                    data=event_data,
                    last_updated=datetime.utcnow(),
                    source=preferred_source
                )
                self.db.add(cached)
            
            # Commit changes
            self.db.commit()
            
            logger.info(f"Cached events for {body_id} from {start_date} to {end_date}")
        except Exception as e:
            # Rollback in case of error
            self.db.rollback()
            logger.error(f"Error caching events for {body_id}: {str(e)}")