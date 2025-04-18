from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class EventEntry(BaseModel):
    """Schema for event entry"""
    id: str = Field(..., description="Event ID")
    name: str = Field(..., description="Event name")

class EventCell(BaseModel):
    """Schema for event cell"""
    date: Optional[str] = Field(None, description="Event date")
    text: Optional[str] = Field(None, description="Event text")

class Event(BaseModel):
    """Schema for astronomical event"""
    entry: EventEntry = Field(..., description="Event entry")
    cells: List[EventCell] = Field(..., description="Event cells")

class EventResponse(BaseModel):
    """Schema for event response"""
    body_id: str = Field(..., description="Body ID")
    events: List[Event] = Field(..., description="List of events")
    cached: bool = Field(..., description="Whether the data was retrieved from cache")
    last_updated: datetime = Field(..., description="When the data was last updated")
    source: str = Field(..., description="Data source (astronomy_api or nasa_api)")