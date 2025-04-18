import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.models import get_db, SearchHistory
from api.schemas.search import SearchHistoryItem, SearchResult
from api.services.api_gateway_service import ApiGatewayService

# Configure logging
logger = logging.getLogger(__name__)

class SearchService:
    """
    Service for handling search functionality.
    
    This service provides methods for searching for celestial bodies
    and retrieving search history.
    """
    
    def __init__(
        self,
        db: Session = Depends(get_db),
        api_gateway: ApiGatewayService = Depends()
    ):
        self.db = db
        self.api_gateway = api_gateway
    
    async def search_bodies(
        self,
        term: str,
        preferred_source: Optional[str] = None
    ) -> List[SearchResult]:
        """
        Search for celestial bodies by name.
        
        Args:
            term: Search term
            preferred_source: Preferred data source
            
        Returns:
            List of matching celestial bodies
        """
        try:
            # Record the search query
            self._record_search(term, preferred_source or "astronomy_api")
            
            # Execute the search
            logger.info(f"Searching for '{term}'")
            results = await self.api_gateway.search_bodies(
                term=term,
                preferred_source=preferred_source
            )
            
            # Convert to response objects
            return [
                SearchResult(
                    id=result["id"],
                    name=result["name"],
                    bodyType=result["bodyType"]
                )
                for result in results
            ]
        except Exception as e:
            logger.error(f"Error searching for '{term}': {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Error searching for bodies: {str(e)}"
            )
    
    def get_search_history(self, limit: int = 10) -> List[SearchHistoryItem]:
        """
        Get recent search history.
        
        Args:
            limit: Maximum number of history items to retrieve
            
        Returns:
            List of search history items
        """
        try:
            # Query search history from the database
            logger.info(f"Retrieving {limit} search history items")
            history = self.db.query(SearchHistory)\
                .order_by(SearchHistory.timestamp.desc())\
                .limit(limit)\
                .all()
            
            # Convert to response format
            return [
                SearchHistoryItem(
                    query=item.query,
                    timestamp=item.timestamp
                )
                for item in history
            ]
        except Exception as e:
            logger.error(f"Error retrieving search history: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving search history: {str(e)}"
            )
    
    def _record_search(self, term: str, source: str) -> None:
        """
        Record a search query in the database.
        
        Args:
            term: Search term
            source: Data source
        """
        try:
            # Create new search history entry
            search_history = SearchHistory(
                query=term,
                timestamp=datetime.utcnow(),
                source=source
            )
            
            # Add to database
            self.db.add(search_history)
            self.db.commit()
            
            logger.info(f"Recorded search for '{term}'")
        except Exception as e:
            # Rollback in case of error
            self.db.rollback()
            logger.error(f"Error recording search for '{term}': {str(e)}")