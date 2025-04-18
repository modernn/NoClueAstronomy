from typing import Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class SearchQuery(BaseModel):
    """Schema for search query"""
    term: str = Field(..., description="Search term")

class SearchResult(BaseModel):
    """Schema for search result"""
    id: str = Field(..., description="Body ID")
    name: str = Field(..., description="Body name")
    bodyType: str = Field(..., description="Body type (Planet, Moon, etc.)")

class SearchResponse(BaseModel):
    """Schema for search response"""
    results: List[SearchResult] = Field(..., description="Search results")

class SearchHistoryItem(BaseModel):
    """Schema for search history item"""
    query: str = Field(..., description="Search query")
    timestamp: datetime = Field(..., description="When the search was performed")

class SearchHistoryResponse(BaseModel):
    """Schema for search history response"""
    history: List[SearchHistoryItem] = Field(..., description="Search history")