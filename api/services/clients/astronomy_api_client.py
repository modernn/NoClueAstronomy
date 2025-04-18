import logging
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from api.services.api.api_client import BaseApiClient
from api.config import (
    ASTRONOMY_API_BASE_URL,
    ASTRONOMY_APP_ID,
    ASTRONOMY_APP_SECRET
)

# Configure logging
logger = logging.getLogger(__name__)

class AstronomyApiClient(BaseApiClient):
    """
    Client for the Astronomy API.
    
    This client handles communication with the Astronomy API,
    including authentication and request formatting.
    """
    
    def __init__(self, base_url: str = ASTRONOMY_API_BASE_URL):
        """
        Initialize the Astronomy API client.
        
        Args:
            base_url: Base URL for API requests
        """
        super().__init__(base_url)
        self.app_id = ASTRONOMY_APP_ID
        self.app_secret = ASTRONOMY_APP_SECRET
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns:
            Dictionary of authentication headers
        """
        # Create Basic Auth string
        auth_str = f"{self.app_id}:{self.app_secret}"
        auth_bytes = auth_str.encode('ascii')
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode('ascii')
        
        return {
            "Authorization": f"Basic {base64_auth}"
        }
    
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
        # Normalize body ID
        normalized_body_id = self._normalize_body_id(body_id)
        
        # Get current date in format YYYY-MM-DD
        current_date = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Prepare request parameters
        params = {
            "body": normalized_body_id,
            "from_date": current_date,
            "to_date": current_date,
            "latitude": latitude,
            "longitude": longitude,
            "elevation": elevation
        }
        
        try:
            # Make API request
            response = await self._make_request(
                "GET",
                "/bodies/positions",
                params=params
            )
            
            # Extract and format body data
            body_data = response.get("data", {}).get("table", {})
            
            # Get the first entry in the table
            body_entry = body_data.get("rows", [{}])[0]
            
            # Format the response
            return {
                "name": self._get_body_name(normalized_body_id),
                "data": {
                    "position": {
                        "equatorial": {
                            "rightAscension": body_entry.get("cells", [])[0].get("position", {}).get("equatorial", {}).get("rightAscension", {}),
                            "declination": body_entry.get("cells", [])[0].get("position", {}).get("equatorial", {}).get("declination", {})
                        },
                        "constellation": body_entry.get("cells", [])[0].get("position", {}).get("constellation", {})
                    },
                    "extraInfo": {
                        "magnitude": body_entry.get("cells", [])[0].get("extraInfo", {}).get("magnitude"),
                        "elongation": body_entry.get("cells", [])[0].get("extraInfo", {}).get("elongation")
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error fetching body {body_id}: {str(e)}")
            raise
    
    async def list_bodies(self) -> List[Dict[str, Any]]:
        """
        List all available celestial bodies.
        
        Returns:
            List of available celestial bodies
        """
        try:
            # Make API request
            response = await self._make_request(
                "GET",
                "/bodies"
            )
            
            # Extract and return body data
            bodies_data = response.get("data", [])
            
            # Format the response
            return [
                {
                    "id": body.get("id"),
                    "name": body.get("name"),
                    "bodyType": body.get("bodyType", {}).get("name", "Unknown")
                }
                for body in bodies_data
            ]
        except Exception as e:
            logger.error(f"Error listing bodies: {str(e)}")
            raise
    
    async def get_events(
        self,
        body_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
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
        # Normalize body ID
        normalized_body_id = self._normalize_body_id(body_id)
        
        # Get current date and date in one month in format YYYY-MM-DD
        now = datetime.utcnow()
        if not start_date:
            start_date = now.strftime("%Y-%m-%d")
        if not end_date:
            end_date = (now + timedelta(days=30)).strftime("%Y-%m-%d")
        
        # For specific bodies, use appropriate endpoints
        if normalized_body_id.lower() == "moon":
            return await self._get_moon_events(start_date, end_date, latitude, longitude, elevation)
        else:
            # For other bodies, fetch opposition, conjunction, etc.
            return await self._get_standard_events(normalized_body_id, start_date, end_date, latitude, longitude, elevation)
    
    async def _get_moon_events(
        self,
        start_date: str,
        end_date: str,
        latitude: float,
        longitude: float,
        elevation: float
    ) -> Dict[str, Any]:
        """
        Get moon phase events.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees
            elevation: Observer elevation in meters
            
        Returns:
            Moon phase events
        """
        # Prepare request parameters
        params = {
            "from_date": start_date,
            "to_date": end_date,
            "latitude": latitude,
            "longitude": longitude,
            "elevation": elevation
        }
        
        try:
            # Make API request
            response = await self._make_request(
                "GET",
                "/studio/moon-phase",
                params=params
            )
            
            # Extract and format moon phase data
            moon_data = response.get("data", {})
            
            # Format the response
            return {
                "body_id": "moon",
                "events": [
                    {
                        "entry": {
                            "id": phase.get("id"),
                            "name": phase.get("name")
                        },
                        "cells": [
                            {
                                "date": phase.get("date"),
                                "text": phase.get("text", "")
                            }
                        ]
                    }
                    for phase in moon_data.get("phaseEvents", [])
                ]
            }
        except Exception as e:
            logger.error(f"Error fetching moon events: {str(e)}")
            raise
    
    async def _get_standard_events(
        self,
        body_id: str,
        start_date: str,
        end_date: str,
        latitude: float,
        longitude: float,
        elevation: float
    ) -> Dict[str, Any]:
        """
        Get standard events for a celestial body.
        
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
        # Prepare request parameters
        params = {
            "body": body_id,
            "from_date": start_date,
            "to_date": end_date,
            "latitude": latitude,
            "longitude": longitude,
            "elevation": elevation
        }
        
        try:
            # Make API request
            response = await self._make_request(
                "GET",
                "/bodies/events",
                params=params
            )
            
            # Extract and format event data
            events_data = response.get("data", {}).get("table", {})
            
            # Format the response
            return {
                "body_id": body_id,
                "events": [
                    {
                        "entry": {
                            "id": row.get("entry", {}).get("id"),
                            "name": row.get("entry", {}).get("name")
                        },
                        "cells": row.get("cells", [])
                    }
                    for row in events_data.get("rows", [])
                ]
            }
        except Exception as e:
            logger.error(f"Error fetching events for {body_id}: {str(e)}")
            raise
    
    async def search_bodies(self, term: str) -> List[Dict[str, Any]]:
        """
        Search for celestial bodies by name.
        
        Args:
            term: Search term
            
        Returns:
            List of matching celestial bodies
        """
        try:
            # First, get the list of all bodies
            all_bodies = await self.list_bodies()
            
            # Filter bodies by search term
            term = term.lower()
            matching_bodies = [
                body for body in all_bodies
                if term in body["id"].lower() or term in body["name"].lower()
            ]
            
            return matching_bodies
        except Exception as e:
            logger.error(f"Error searching for '{term}': {str(e)}")
            raise
    
    async def check_health(self) -> bool:
        """
        Check the health of the Astronomy API.
        
        Returns:
            Whether the API is healthy
        """
        try:
            # Try to list bodies as a health check
            await self._make_request("GET", "/bodies")
            return True
        except Exception as e:
            logger.error(f"Health check failed for Astronomy API: {str(e)}")
            return False
    
    def _normalize_body_id(self, body_id: str) -> str:
        """
        Normalize body ID to Astronomy API format.
        
        Args:
            body_id: Original body ID
            
        Returns:
            Normalized body ID
        """
        # Map common body IDs to Astronomy API format
        mapping = {
            "sun": "sun",
            "mercury": "mercury",
            "venus": "venus",
            "earth": "earth",
            "moon": "moon",
            "mars": "mars",
            "jupiter": "jupiter",
            "saturn": "saturn",
            "uranus": "uranus",
            "neptune": "neptune",
            "pluto": "pluto"
        }
        
        return mapping.get(body_id.lower(), body_id)
    
    def _get_body_name(self, body_id: str) -> str:
        """
        Get the display name for a body ID.
        
        Args:
            body_id: Body ID
            
        Returns:
            Body display name
        """
        # Map body IDs to display names
        mapping = {
            "sun": "Sun",
            "mercury": "Mercury",
            "venus": "Venus",
            "earth": "Earth",
            "moon": "Moon",
            "mars": "Mars",
            "jupiter": "Jupiter",
            "saturn": "Saturn",
            "uranus": "Uranus",
            "neptune": "Neptune",
            "pluto": "Pluto"
        }
        
        return mapping.get(body_id.lower(), body_id.capitalize())