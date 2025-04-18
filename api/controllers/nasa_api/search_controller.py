from fastapi import Depends, Query
from typing import Optional

from api.controllers.nasa_api.base_controller import BaseController
from api.services.api.nasa_api_client import NasaApiClient
from api.services.search_service import SearchService
from api.schemas.search import SearchQuery, SearchResponse, SearchHistoryResponse

class SearchController(BaseController):
    """
    Controller for NASA API search endpoints.
    
    This controller handles requests related to searching for celestial bodies
    and retrieving search history from the NASA API.
    """
    
    def __init__(self):
        super().__init__(router_prefix="/nasa/search", tags=["NASA Search"])
    
    def _register_routes(self) -> None:
        """Register all routes for the NASA search controller"""
        
        @self.router.post("", response_model=SearchResponse)
        async def search_bodies(
            query: SearchQuery,
            nasa_client: NasaApiClient = Depends(),
            search_service: SearchService = Depends()
        ):
            """
            Search for celestial bodies by name using NASA API.
            
            Searches for celestial bodies by name and returns a list of matching bodies
            from the NASA API. The search is case-insensitive and matches any part of the name or ID.
            Search queries are recorded for analytics purposes.
            """
            # Record the search in history (using the search service)
            search_service._record_search(query.term, "nasa_api")
            
            # Perform the search using NASA API client
            results = await nasa_client.search_bodies(term=query.term)
            
            return SearchResponse(results=results)
        
        @self.router.get("/history", response_model=SearchHistoryResponse)
        async def get_search_history(
            limit: int = Query(10, description="Maximum number of history items to retrieve"),
            search_service: SearchService = Depends()
        ):
            """
            Get recent NASA API search history.
            
            Retrieves a list of recent NASA API search queries, ordered by timestamp (newest first).
            Only returns searches that were performed using the NASA API source.
            """
            # Get all search history
            all_history = search_service.get_search_history(limit=limit * 2)
            
            # Filter for NASA API searches only
            nasa_history = [
                item for item in all_history 
                if hasattr(item, 'source') and item.source == "nasa_api"
            ][:limit]
            
            return SearchHistoryResponse(history=nasa_history)