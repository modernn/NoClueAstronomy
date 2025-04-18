import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.models import get_db, CachedBody
from api.schemas.body import BodyResponse, BodyListResponse
from api.services.api_gateway_service import ApiGatewayService
from api.config import CACHE_EXPIRATION_HOURS

# Configure logging
logger = logging.getLogger(__name__)

class BodyService:
    """
    Service for handling celestial body data.
    
    This service provides methods for retrieving and caching
    information about celestial bodies.
    """
    
    def __init__(
        self, 
        db: Session = Depends(get_db),
        api_gateway: ApiGatewayService = Depends()
    ):
        self.db = db
        self.api_gateway = api_gateway
    
    async def get_body(
        self,
        body_id: str,
        force_refresh: bool = False,
        preferred_source: Optional[str] = None,
        latitude: float = 0.0,
        longitude: float = 0.0,
        elevation: float = 0.0
    ) -> BodyResponse:
        """
        Get information about a specific celestial body.
        
        Args:
            body_id: ID of the celestial body
            force_refresh: Whether to force refresh cached data
            preferred_source: Preferred data source
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees
            elevation: Observer elevation in meters
            
        Returns:
            Information about the celestial body
        """
        # Check cache if not forcing refresh
        if not force_refresh:
            cached_body = self._get_cached_body(body_id)
            if cached_body:
                logger.info(f"Retrieved {body_id} from cache")
                return cached_body
        
        # Fetch fresh data
        try:
            logger.info(f"Fetching fresh data for {body_id}")
            body_data = await self.api_gateway.get_body(
                body_id=body_id,
                preferred_source=preferred_source,
                latitude=latitude,
                longitude=longitude,
                elevation=elevation
            )
            
            # Cache the result
            self._cache_body(body_id, body_data, preferred_source or "astronomy_api")
            
            return BodyResponse(
                id=body_id,
                name=body_data["name"],
                data=body_data["data"],
                cached=False,
                last_updated=datetime.utcnow(),
                source=preferred_source or "astronomy_api"
            )
        except Exception as e:
            logger.error(f"Error fetching {body_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error fetching body data: {str(e)}"
            )
    
    async def get_multiple_bodies(
        self,
        body_ids: List[str],
        force_refresh: bool = False,
        preferred_source: Optional[str] = None
    ) -> List[BodyResponse]:
        """
        Get information about multiple celestial bodies.
        
        Args:
            body_ids: List of body IDs
            force_refresh: Whether to force refresh cached data
            preferred_source: Preferred data source
            
        Returns:
            List of body information
        """
        results = []
        
        # Process each body ID
        for body_id in body_ids:
            try:
                body_data = await self.get_body(
                    body_id=body_id,
                    force_refresh=force_refresh,
                    preferred_source=preferred_source
                )
                results.append(body_data)
            except Exception as e:
                logger.error(f"Error fetching {body_id}: {str(e)}")
                # Create a placeholder response for failed bodies
                results.append(
                    BodyResponse(
                        id=body_id,
                        name=body_id.capitalize(),
                        data={"error": f"Failed to fetch data: {str(e)}"},
                        cached=False,
                        last_updated=datetime.utcnow(),
                        source="error"
                    )
                )
        
        return results
    
    async def list_bodies(
        self,
        preferred_source: Optional[str] = None
    ) -> BodyListResponse:
        """
        List all available celestial bodies.
        
        Args:
            preferred_source: Preferred data source
            
        Returns:
            List of available celestial bodies
        """
        try:
            # Try to get from cache first
            cache_key = f"body_list_{preferred_source or 'default'}"
            cached_list = self._get_cached_body(cache_key)
            
            if cached_list:
                logger.info("Retrieved body list from cache")
                return BodyListResponse(bodies=cached_list.data["bodies"])
            
            # Fetch fresh data
            logger.info("Fetching fresh body list")
            body_list = await self.api_gateway.list_bodies(
                preferred_source=preferred_source
            )
            
            # Cache the result
            self._cache_body(
                cache_key, 
                {"name": "Body List", "data": {"bodies": body_list}},
                preferred_source or "astronomy_api"
            )
            
            return BodyListResponse(bodies=body_list)
        except Exception as e:
            logger.error(f"Error listing bodies: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error listing bodies: {str(e)}"
            )
    
    def _get_cached_body(self, body_id: str) -> Optional[BodyResponse]:
        """
        Get a cached body if it exists and is not expired.
        
        Args:
            body_id: ID of the celestial body
            
        Returns:
            Cached body or None if not found or expired
        """
        # Find the cached body in the database
        cached = self.db.query(CachedBody).filter(CachedBody.id == body_id).first()
        
        if not cached:
            return None
        
        # Check if the cache is expired
        expiration_time = cached.last_updated + timedelta(hours=CACHE_EXPIRATION_HOURS)
        if datetime.utcnow() > expiration_time:
            return None
        
        # Return the cached body
        return BodyResponse(
            id=body_id,
            name=cached.data["name"],
            data=cached.data["data"],
            cached=True,
            last_updated=cached.last_updated,
            source=cached.source
        )
    
    def _cache_body(
        self,
        body_id: str,
        body_data: Dict[str, Any],
        source: str
    ) -> None:
        """
        Cache body data in the database.
        
        Args:
            body_id: ID of the celestial body
            body_data: Body data to cache
            source: Data source
        """
        try:
            # Check if the body is already cached
            cached = self.db.query(CachedBody).filter(CachedBody.id == body_id).first()
            
            if cached:
                # Update existing cache
                cached.data = body_data
                cached.last_updated = datetime.utcnow()
                cached.source = source
            else:
                # Create new cache entry
                cached = CachedBody(
                    id=body_id,
                    data=body_data,
                    last_updated=datetime.utcnow(),
                    source=source
                )
                self.db.add(cached)
            
            # Commit changes
            self.db.commit()
            
            logger.info(f"Cached {body_id}")
        except Exception as e:
            # Rollback in case of error
            self.db.rollback()
            logger.error(f"Error caching {body_id}: {str(e)}")