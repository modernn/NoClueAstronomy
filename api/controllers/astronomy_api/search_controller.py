from fastapi import Depends, Query
from typing import Optional

from api.controllers.astronomy_api.base_controller import BaseController
from api.services.search_service import SearchService
from api.schemas.search import SearchQuery, SearchResponse, SearchHistoryResponse

class SearchController(BaseController):
    """
    Controller for search endpoints using Astronomy API.
    
    This controller handles requests related to searching for celestial bodies
    and retrieving search history.
    """
    
    def __init__(self):
        super().__init__(router_prefix="/astronomy/search", tags=["Astronomy Search"])
    
    def _register_routes(self) -> None:
        """Register all routes for the search controller"""
        
        @self.router.post("", response_model=SearchResponse)
        async def search_bodies(
            query: SearchQuery,
            search_service: SearchService = Depends()
        ):
            """
            Search for celestial bodies by name using Astronomy API.
            
            Searches for celestial bodies by name and returns a list of matching bodies.
            The search is case-insensitive and matches any part of the name or ID.
            """
            results = await search_service.search_bodies(
                term=query.term,
                preferred_source="astronomy_api"
            )
            
            return SearchResponse(results=results)
        
        @self.router.get("/history", response_model=SearchHistoryResponse)
        async def get_search_history(
            limit: int = Query(10, description="Maximum number of history items to retrieve"),
            search_service: SearchService = Depends()
        ):
            """
            Get recent search history from Astronomy API.
            
            Retrieves a list of recent search queries, ordered by timestamp (newest first).
            """
            history = search_service.get_search_history(limit=limit)
            
            return SearchHistoryResponse(history=history)