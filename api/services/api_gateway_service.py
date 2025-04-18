import logging
from typing import Dict, Any, List, Optional

from fastapi import Depends, HTTPException, status

from api.services.api.astronomy_api_client import AstronomyApiClient
from api.services.api.nasa_api_client import NasaApiClient

# Configure logging
logger = logging.getLogger(__name__)

class ApiGatewayService:
    """
    Gateway service for external API communication.
    
    This service acts as a facade for all external API clients,
    providing fallback functionality and a unified interface.
    """
    
    def __init__(
        self,
        astronomy_api: AstronomyApiClient = Depends(),
        nasa_api: NasaApiClient = Depends()
    ):
        self.clients = {
            "astronomy_api": astronomy_api,
            "nasa_api": nasa_api
        }
    
    async def get_body(
        self,
        body_id: str,
        preferred_source: Optional[str] = None,
        latitude: float = 0.0,
        longitude: float = 0.0,
        elevation: float = 0.0
    ) -> Dict[str, Any]:
        """
        Get information about a specific celestial body.
        
        Args:
            body_id: ID of the celestial body
            preferred_source: Preferred data source
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees
            elevation: Observer elevation in meters
            
        Returns:
            Body information
            
        Raises:
            HTTPException: If all data sources fail
        """
        # Determine the order of clients to try
        client_order = self._get_client_order(preferred_source)
        
        errors = {}
        for source in client_order:
            try:
                # Try to get the body from this source
                client = self.clients[source]
                body_data = await client.get_body(
                    body_id=body_id,
                    latitude=latitude,
                    longitude=longitude,
                    elevation=elevation
                )
                logger.info(f"Retrieved {body_id} from {source}")
                return body_data
            except Exception as e:
                # Log the error and try the next source
                logger.warning(f"Error retrieving {body_id} from {source}: {str(e)}")
                errors[source] = str(e)
        
        # If we get here, all sources failed
        error_details = ", ".join([f"{s}: {e}" for s, e in errors.items()])
        logger.error(f"All sources failed for {body_id}: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to retrieve body data from any source: {error_details}"
        )
    
    async def get_multiple_bodies(
        self,
        body_ids: List[str],
        preferred_source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get information about multiple celestial bodies.
        
        This method tries to use API batch endpoints if available,
        falling back to individual requests if needed.
        
        Args:
            body_ids: List of body IDs
            preferred_source: Preferred data source
            
        Returns:
            Dictionary mapping body IDs to body information
        """
        # Determine the order of clients to try
        client_order = self._get_client_order(preferred_source)
        
        # Try to use batch endpoints if available
        for source in client_order:
            client = self.clients[source]
            try:
                # Check if the client supports batch retrieval
                if hasattr(client, 'get_multiple_bodies'):
                    bodies_data = await client.get_multiple_bodies(body_ids=body_ids)
                    logger.info(f"Retrieved multiple bodies from {source}")
                    return bodies_data
            except Exception as e:
                logger.warning(f"Error retrieving multiple bodies from {source}: {str(e)}")
        
        # Fallback to individual requests
        logger.info("Falling back to individual requests for multiple bodies")
        results = {}
        for body_id in body_ids:
            try:
                body_data = await self.get_body(
                    body_id=body_id,
                    preferred_source=preferred_source
                )
                results[body_id] = body_data
            except Exception as e:
                logger.error(f"Error retrieving {body_id}: {str(e)}")
                results[body_id] = {"error": str(e)}
        
        return results
    
    async def list_bodies(
        self,
        preferred_source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all available celestial bodies.
        
        Args:
            preferred_source: Preferred data source
            
        Returns:
            List of available celestial bodies
            
        Raises:
            HTTPException: If all data sources fail
        """
        # Determine the order of clients to try
        client_order = self._get_client_order(preferred_source)
        
        errors = {}
        for source in client_order:
            try:
                # Try to list bodies from this source
                client = self.clients[source]
                bodies = await client.list_bodies()
                logger.info(f"Listed bodies from {source}")
                return bodies
            except Exception as e:
                # Log the error and try the next source
                logger.warning(f"Error listing bodies from {source}: {str(e)}")
                errors[source] = str(e)
        
        # If we get here, all sources failed
        error_details = ", ".join([f"{s}: {e}" for s, e in errors.items()])
        logger.error(f"All sources failed to list bodies: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to list bodies from any source: {error_details}"
        )
    
    async def get_events(
        self,
        body_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        preferred_source: Optional[str] = None,
        latitude: float = 0.0,
        longitude: float = 0.0,
        elevation: float = 0.0
    ) -> Dict[str, Any]:
        """
        Get events for a specific celestial body.
        
        Args:
            body_id: ID of the celestial body
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            preferred_source: Preferred data source
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees
            elevation: Observer elevation in meters
            
        Returns:
            Events for the celestial body
            
        Raises:
            HTTPException: If all data sources fail
        """
        # Determine the order of clients to try
        client_order = self._get_client_order(preferred_source)
        
        errors = {}
        for source in client_order:
            try:
                # Try to get events from this source
                client = self.clients[source]
                events = await client.get_events(
                    body_id=body_id,
                    start_date=start_date,
                    end_date=end_date,
                    latitude=latitude,
                    longitude=longitude,
                    elevation=elevation
                )
                logger.info(f"Retrieved events for {body_id} from {source}")
                return events
            except Exception as e:
                # Log the error and try the next source
                logger.warning(f"Error retrieving events for {body_id} from {source}: {str(e)}")
                errors[source] = str(e)
        
        # If we get here, all sources failed
        error_details = ", ".join([f"{s}: {e}" for s, e in errors.items()])
        logger.error(f"All sources failed to get events for {body_id}: {error_details}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to retrieve events from any source: {error_details}"
        )
    
    async def search_bodies(
        self,
        term: str,
        preferred_source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for celestial bodies by name.
        
        Args:
            term: Search term
            preferred_source: Preferred data source
            
        Returns:
            List of matching celestial bodies
            
        Raises:
            HTTPException: If all data sources fail
        """
        # Determine the order of clients to try
        client_order = self._get_client_order(preferred_source)
        
        errors = {}
        for source in client_order:
            try:
                # Try to search from this source
                client = self.clients[source]
                results = await client.search_bodies(term=term)
                logger.info(f"Searched for '{term}' in {source}")
                return results
            except Exception as e:
                # Log the error and try the next source
                logger.warning(f"Error searching for '{term}' in {source}: {str(e)}")
                errors[source] = str(e)
        
        # If we get here, all sources failed
        error_details = ", ".join([f"{s}: {e}" for s, e in errors.items()])
        logger.error(f"All sources failed to search for '{term}': {error_details}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to search from any source: {error_details}"
        )
    
    async def check_health(self) -> Dict[str, bool]:
        """
        Check the health of all API clients.
        
        Returns:
            Dictionary mapping client names to health status
        """
        health = {}
        
        for source, client in self.clients.items():
            try:
                health[source] = await client.check_health()
            except Exception as e:
                logger.error(f"Error checking health of {source}: {str(e)}")
                health[source] = False
        
        return health
    
    def _get_client_order(self, preferred_source: Optional[str] = None) -> List[str]:
        """
        Determine the order of clients to try based on preference.
        
        Args:
            preferred_source: Preferred data source
            
        Returns:
            List of client names in order of preference
        """
        # Define the default order
        default_order = ["astronomy_api", "nasa_api"]
        
        # Return all available clients with preferred source first
        if preferred_source and preferred_source in self.clients:
            # Create a new list with preferred source first
            return [preferred_source] + [s for s in default_order if s != preferred_source]
        
        # Return default order
        return default_order