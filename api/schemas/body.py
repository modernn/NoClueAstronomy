from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PositionEquatorial(BaseModel):
    """Schema for equatorial position"""
    rightAscension: Dict[str, str] = Field(..., description="Right ascension (hours)")
    declination: Dict[str, str] = Field(..., description="Declination (degrees)")

class Constellation(BaseModel):
    """Schema for constellation"""
    id: str = Field(..., description="Constellation ID")
    short: str = Field(..., description="Constellation short name")
    name: str = Field(..., description="Constellation full name")

class Position(BaseModel):
    """Schema for celestial body position"""
    equatorial: PositionEquatorial = Field(..., description="Equatorial coordinates")
    constellation: Constellation = Field(..., description="Constellation information")

class BodyData(BaseModel):
    """Schema for celestial body data"""
    position: Position = Field(..., description="Position information")
    extraInfo: Optional[Dict[str, Any]] = Field(None, description="Additional information")

class BodyResponse(BaseModel):
    """Schema for body response"""
    id: str = Field(..., description="Body ID")
    name: str = Field(..., description="Body name")
    data: BodyData = Field(..., description="Body data")
    cached: bool = Field(..., description="Whether the data was retrieved from cache")
    last_updated: datetime = Field(..., description="When the data was last updated")
    source: str = Field(..., description="Data source (astronomy_api or nasa_api)")

class BodyInfo(BaseModel):
    """Schema for basic body information"""
    id: str = Field(..., description="Body ID")
    name: str = Field(..., description="Body name")
    bodyType: str = Field(..., description="Body type (Planet, Moon, etc.)")

class BodyListResponse(BaseModel):
    """Schema for body list response"""
    bodies: List[BodyInfo] = Field(..., description="List of available bodies")
