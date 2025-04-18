import logging
import aiohttp
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

# Configure logging
logger = logging.getLogger(__name__)

class BaseApiClient(ABC):
    """
    Base API client class for external API communication.
    
    This abstract class defines the common interface and utility methods
    for all API clients. Specific API clients should inherit from this
    class and implement the abstract methods.
    """
    
    def __init__(self, base_url: str):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL for API requests
        """
        self.base_url = base_url
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            headers: Request headers
            
        Returns:
            API response data
        
        Raises:
            Exception: If the API request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        # Create default headers if none provided
        if headers is None:
            headers = {}
        
        # Add request authentication headers
        auth_headers = self._get_auth_headers()
        if auth_headers:
            headers.update(auth_headers)
        
        try:
            logger.debug(f"Making {method} request to {url}")
            
            async with aiohttp.ClientSession() as session:
                request_kwargs = {
                    "params": params,
                    "headers": headers
                }
                
                if data is not None:
                    request_kwargs["json"] = data
                
                async with session.request(method, url, **request_kwargs) as response:
                    response_text = await response.text()
                    
                    if response.status < 200 or response.status >= 300:
                        logger.error(f"API request failed: {response.status} - {response_text}")
                        raise Exception(f"API request failed: {response.status} - {response_text}")
                    
                    # Try to parse response as JSON
                    try:
                        return await response.json()
                    except ValueError:
                        logger.warning(f"API response is not valid JSON: {response_text}")
                        return {"raw_response": response_text}
        
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error during API request: {str(e)}")
            raise Exception(f"HTTP error during API request: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error during API request: {str(e)}")
            raise
    
    @abstractmethod
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns:
            Dictionary of authentication headers
        """
        pass
    
    @abstractmethod
    async def get_body(
        self,
        body_id: str,
        latitude: float = 0.0,
        longitude: float = 0.0,
        elevation: float = 0.0
    ) -> Dict[str, Any]:
        """
        Get information about a specific celestial body.
        
        Args:
            body_id: ID of the celestial body
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees
            elevation: Observer elevation in meters
            
        Returns:
            Body information
        """
        pass
    
    @abstractmethod
    async def list_bodies(self) -> List[Dict[str, Any]]:
        """
        List all available celestial bodies.
        
        Returns:
            List of available celestial bodies
        """
        pass
    
    @abstractmethod
    async def get_events(
        self,
        body_id: str,
        start_date: Optional[str],
        end_date: Optional[str],
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
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees
            elevation: Observer elevation in meters
            
        Returns:
            Events for the celestial body
        """
        pass
    
    @abstractmethod
    async def search_bodies(self, term: str) -> List[Dict[str, Any]]:
        """
        Search for celestial bodies by name.
        
        Args:
            term: Search term
            
        Returns:
            List of matching celestial bodies
        """
        pass
    
    @abstractmethod
    async def check_health(self) -> bool:
        """
        Check the health of the API.
        
        Returns:
            Whether the API is healthy
        """
        pass