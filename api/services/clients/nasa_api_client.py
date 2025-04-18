import logging
import aiohttp
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from api.services.api.api_client import BaseApiClient
from api.config import (
    NASA_API_BASE_URL,
    NASA_API_KEY
)

# Configure logging
logger = logging.getLogger(__name__)

class NasaApiClient(BaseApiClient):
    """
    Client for the NASA API.
    
    This client handles communication with the NASA API,
    including authentication and request formatting.
    """
    
    def __init__(self, base_url: str = NASA_API_BASE_URL):
        """
        Initialize the NASA API client.
        
        Args:
            base_url: Base URL for API requests
        """
        super().__init__(base_url)
        self.api_key = NASA_API_KEY
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns:
            Dictionary of authentication headers
        """
        # NASA API uses API key in query parameters rather than headers
        return {}
    
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
        
        # NASA API doesn't have a direct equivalent to the Astronomy API's body positions
        # We'll use a combination of endpoints to gather similar information
        
        try:
            # For planets, use the NASA Solar System Dynamics API
            if normalized_body_id in ["mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]:
                return await self._get_planet_info(normalized_body_id, latitude, longitude, elevation)
            
            # For the moon, use a different endpoint
            elif normalized_body_id == "moon":
                return await self._get_moon_info(latitude, longitude, elevation)
            
            # For the sun, use a different approach
            elif normalized_body_id == "sun":
                return await self._get_sun_info(latitude, longitude, elevation)
            
            # For other bodies, provide a more generic response
            else:
                return await self._get_generic_body_info(normalized_body_id)
        
        except Exception as e:
            logger.error(f"Error fetching body {body_id} from NASA API: {str(e)}")
            raise
    
    async def list_bodies(self) -> List[Dict[str, Any]]:
        """
        List all available celestial bodies.
        
        Returns:
            List of available celestial bodies
        """
        # NASA API doesn't have a direct endpoint for listing all bodies
        # We'll return a predefined list of commonly supported bodies
        
        try:
            # Return a static list of common celestial bodies
            return [
                {"id": "sun", "name": "Sun", "bodyType": "Star"},
                {"id": "mercury", "name": "Mercury", "bodyType": "Planet"},
                {"id": "venus", "name": "Venus", "bodyType": "Planet"},
                {"id": "earth", "name": "Earth", "bodyType": "Planet"},
                {"id": "moon", "name": "Moon", "bodyType": "Moon"},
                {"id": "mars", "name": "Mars", "bodyType": "Planet"},
                {"id": "jupiter", "name": "Jupiter", "bodyType": "Planet"},
                {"id": "saturn", "name": "Saturn", "bodyType": "Planet"},
                {"id": "uranus", "name": "Uranus", "bodyType": "Planet"},
                {"id": "neptune", "name": "Neptune", "bodyType": "Planet"},
                {"id": "pluto", "name": "Pluto", "bodyType": "Dwarf Planet"}
            ]
        
        except Exception as e:
            logger.error(f"Error listing bodies from NASA API: {str(e)}")
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
        
        # Set default dates if not provided
        now = datetime.utcnow()
        if not start_date:
            start_date = now.strftime("%Y-%m-%d")
        if not end_date:
            end_date = (now + timedelta(days=30)).strftime("%Y-%m-%d")
        
        try:
            # For moon, use specific logic for moon phases
            if normalized_body_id == "moon":
                return await self._get_moon_events(start_date, end_date)
            
            # For planets, use a different approach
            else:
                return await self._get_planet_events(normalized_body_id, start_date, end_date)
        
        except Exception as e:
            logger.error(f"Error fetching events for {body_id} from NASA API: {str(e)}")
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
            # Get the list of supported bodies
            all_bodies = await self.list_bodies()
            
            # Filter bodies based on the search term
            term_lower = term.lower()
            matching_bodies = [
                body for body in all_bodies
                if term_lower in body["id"].lower() or term_lower in body["name"].lower()
            ]
            
            return matching_bodies
        
        except Exception as e:
            logger.error(f"Error searching for '{term}' in NASA API: {str(e)}")
            raise
    
    async def check_health(self) -> bool:
        """
        Check the health of the NASA API.
        
        Returns:
            Whether the API is healthy
        """
        try:
            # We'll use a simple API endpoint to check if the NASA API is working
            params = {"api_key": self.api_key}
            
            # Try to query the APOD (Astronomy Picture of the Day) API as a health check
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/planetary/apod"
                async with session.get(url, params=params) as response:
                    return response.status == 200
        
        except Exception as e:
            logger.error(f"Health check failed for NASA API: {str(e)}")
            return False
    
    async def _get_planet_info(
        self,
        planet_id: str,
        latitude: float,
        longitude: float,
        elevation: float
    ) -> Dict[str, Any]:
        """
        Get detailed information about a planet.
        
        Args:
            planet_id: Planet ID
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees
            elevation: Observer elevation in meters
            
        Returns:
            Planet information
        """
        # Use HORIZONS API (through a NASA API endpoint) to get position data
        # In a real implementation, we'd make an actual API call here
        
        # For demonstration, we'll return placeholder data formatted like the Astronomy API
        return {
            "name": self._get_body_name(planet_id),
            "data": {
                "position": {
                    "equatorial": {
                        "rightAscension": {
                            "hours": "12.5",
                            "string": "12h 30m 0s"
                        },
                        "declination": {
                            "degrees": "15.0",
                            "string": "15° 0' 0\""
                        }
                    },
                    "constellation": {
                        "id": "vir",
                        "short": "Vir",
                        "name": "Virgo"
                    }
                },
                "extraInfo": {
                    "magnitude": 0.5,
                    "elongation": 45.0
                }
            }
        }
    
    async def _get_moon_info(
        self,
        latitude: float,
        longitude: float,
        elevation: float
    ) -> Dict[str, Any]:
        """
        Get detailed information about the Moon.
        
        Args:
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees
            elevation: Observer elevation in meters
            
        Returns:
            Moon information
        """
        # In a real implementation, we'd make an actual API call here
        
        # For demonstration, we'll return placeholder data formatted like the Astronomy API
        return {
            "name": "Moon",
            "data": {
                "position": {
                    "equatorial": {
                        "rightAscension": {
                            "hours": "14.5",
                            "string": "14h 30m 0s"
                        },
                        "declination": {
                            "degrees": "-10.0",
                            "string": "-10° 0' 0\""
                        }
                    },
                    "constellation": {
                        "id": "lib",
                        "short": "Lib",
                        "name": "Libra"
                    }
                },
                "extraInfo": {
                    "magnitude": -12.5,
                    "elongation": 90.0
                }
            }
        }
    
    async def _get_sun_info(
        self,
        latitude: float,
        longitude: float,
        elevation: float
    ) -> Dict[str, Any]:
        """
        Get detailed information about the Sun.
        
        Args:
            latitude: Observer latitude in degrees
            longitude: Observer longitude in degrees
            elevation: Observer elevation in meters
            
        Returns:
            Sun information
        """
        # In a real implementation, we'd make an actual API call here
        
        # For demonstration, we'll return placeholder data formatted like the Astronomy API
        return {
            "name": "Sun",
            "data": {
                "position": {
                    "equatorial": {
                        "rightAscension": {
                            "hours": "10.0",
                            "string": "10h 0m 0s"
                        },
                        "declination": {
                            "degrees": "15.0",
                            "string": "15° 0' 0\""
                        }
                    },
                    "constellation": {
                        "id": "leo",
                        "short": "Leo",
                        "name": "Leo"
                    }
                },
                "extraInfo": {
                    "magnitude": -26.7,
                    "elongation": 0.0
                }
            }
        }
    
    async def _get_generic_body_info(self, body_id: str) -> Dict[str, Any]:
        """
        Get generic information about a celestial body.
        
        Args:
            body_id: Body ID
            
        Returns:
            Generic body information
        """
        # For bodies not specifically handled, we'll use the NASA Image API to get some information
        # In a real implementation, we'd make an actual API call here
        
        # For demonstration, we'll return placeholder data formatted like the Astronomy API
        return {
            "name": body_id.capitalize(),
            "data": {
                "position": {
                    "equatorial": {
                        "rightAscension": {
                            "hours": "0.0",
                            "string": "0h 0m 0s"
                        },
                        "declination": {
                            "degrees": "0.0",
                            "string": "0° 0' 0\""
                        }
                    },
                    "constellation": {
                        "id": "and",
                        "short": "And",
                        "name": "Andromeda"
                    }
                },
                "extraInfo": {
                    "magnitude": None,
                    "elongation": None
                }
            }
        }
    
    async def _get_moon_events(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get moon phase events.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Moon phase events
        """
        # In a real implementation, we'd calculate or fetch actual moon phases
        # For demonstration, we'll return placeholder data formatted like the Astronomy API
        
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Generate some sample events in the date range
        events = []
        
        # Add sample new moon
        new_moon_date = datetime(start.year, start.month, 15)
        if start <= new_moon_date <= end:
            events.append({
                "entry": {
                    "id": "new_moon",
                    "name": "New Moon"
                },
                "cells": [
                    {
                        "date": new_moon_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "text": f"New Moon on {new_moon_date.strftime('%B %d, %Y')}"
                    }
                ]
            })
        
        # Add sample full moon
        full_moon_date = datetime(start.year, start.month, 1)
        if start <= full_moon_date <= end:
            events.append({
                "entry": {
                    "id": "full_moon",
                    "name": "Full Moon"
                },
                "cells": [
                    {
                        "date": full_moon_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "text": f"Full Moon on {full_moon_date.strftime('%B %d, %Y')}"
                    }
                ]
            })
        
        # Add sample first quarter
        first_quarter_date = datetime(start.year, start.month, 8)
        if start <= first_quarter_date <= end:
            events.append({
                "entry": {
                    "id": "first_quarter",
                    "name": "First Quarter"
                },
                "cells": [
                    {
                        "date": first_quarter_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "text": f"First Quarter on {first_quarter_date.strftime('%B %d, %Y')}"
                    }
                ]
            })
        
        # Add sample last quarter
        last_quarter_date = datetime(start.year, start.month, 22)
        if start <= last_quarter_date <= end:
            events.append({
                "entry": {
                    "id": "last_quarter",
                    "name": "Last Quarter"
                },
                "cells": [
                    {
                        "date": last_quarter_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "text": f"Last Quarter on {last_quarter_date.strftime('%B %d, %Y')}"
                    }
                ]
            })
        
        return {
            "body_id": "moon",
            "events": events
        }
    
    async def _get_planet_events(self, planet_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Get events for a planet.
        
        Args:
            planet_id: Planet ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            Planet events
        """
        # In a real implementation, we'd calculate or fetch actual planetary events
        # For demonstration, we'll return placeholder data formatted like the Astronomy API
        
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Generate some sample events in the date range
        events = []
        
        # Add sample opposition (for outer planets)
        if planet_id in ["mars", "jupiter", "saturn", "uranus", "neptune", "pluto"]:
            opposition_date = datetime(start.year, start.month, 10)
            if start <= opposition_date <= end:
                events.append({
                    "entry": {
                        "id": "opposition",
                        "name": "Opposition"
                    },
                    "cells": [
                        {
                            "date": opposition_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "text": f"{self._get_body_name(planet_id)} at Opposition on {opposition_date.strftime('%B %d, %Y')}"
                        }
                    ]
                })
        
        # Add sample conjunction (for all planets)
        conjunction_date = datetime(start.year, start.month, 20)
        if start <= conjunction_date <= end:
            events.append({
                "entry": {
                    "id": "conjunction",
                    "name": "Conjunction"
                },
                "cells": [
                    {
                        "date": conjunction_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "text": f"{self._get_body_name(planet_id)} at Conjunction on {conjunction_date.strftime('%B %d, %Y')}"
                    }
                ]
            })
        
        return {
            "body_id": planet_id,
            "events": events
        }
    
    def _normalize_body_id(self, body_id: str) -> str:
        """
        Normalize body ID to NASA API format.
        
        Args:
            body_id: Original body ID
            
        Returns:
            Normalized body ID
        """
        # Map common body IDs to NASA API format
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