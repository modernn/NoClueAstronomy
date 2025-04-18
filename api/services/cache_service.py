import logging
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import Depends
from sqlalchemy.orm import Session

from app.models import get_db, CachedBody, CachedEvent, SearchHistory

# Configure logging
logger = logging.getLogger(__name__)

class CacheService:
    """
    Service for managing cache operations.
    
    This service provides methods for getting cache statistics
    and clearing the cache.
    """
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the cache.
        
        Returns:
            Dictionary containing cache statistics
        """
        body_count = self.db.query(CachedBody).count()
        event_count = self.db.query(CachedEvent).count()
        search_count = self.db.query(SearchHistory).count()
        
        oldest_body_cache = self.db.query(CachedBody).order_by(CachedBody.last_updated).first()
        oldest_event_cache = self.db.query(CachedEvent).order_by(CachedEvent.last_updated).first()
        
        return {
            "bodies_cached": body_count,
            "events_cached": event_count,
            "searches_recorded": search_count,
            "oldest_body_cache": oldest_body_cache.last_updated if oldest_body_cache else None,
            "oldest_event_cache": oldest_event_cache.last_updated if oldest_event_cache else None
        }
    
    def clear_cache(self, clear_search_history: bool = False) -> Dict[str, Any]:
        """
        Clear all cached data.
        
        Args:
            clear_search_history: Whether to also clear search history
            
        Returns:
            Dictionary containing information about the operation
        """
        try:
            body_count = self.db.query(CachedBody).count()
            event_count = self.db.query(CachedEvent).count()
            search_count = 0
            
            # Clear cached bodies
            self.db.query(CachedBody).delete()
            
            # Clear cached events
            self.db.query(CachedEvent).delete()
            
            # Optionally clear search history
            if clear_search_history:
                search_count = self.db.query(SearchHistory).count()
                self.db.query(SearchHistory).delete()
            
            # Commit changes
            self.db.commit()
            
            logger.info(f"Cache cleared: {body_count} bodies, {event_count} events, {search_count} search history items")
            
            return {
                "message": "Cache cleared successfully",
                "bodies_cleared": body_count,
                "events_cleared": event_count,
                "search_history_cleared": search_count if clear_search_history else 0
            }
        except Exception as e:
            # Rollback in case of error
            self.db.rollback()
            logger.error(f"Error clearing cache: {str(e)}")
            raise