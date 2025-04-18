from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func

from api.models.db import Base

class CachedBody(Base):
    """
    Model for cached celestial body data.
    
    This model stores cached information about celestial bodies,
    including their position, distance, and other properties.
    """
    
    __tablename__ = "cached_bodies"
    
    body_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    last_updated = Column(DateTime, default=func.now(), nullable=False)
    source = Column(String, nullable=False)
    
    def __repr__(self):
        """Return string representation of the model."""
        return f"<CachedBody(body_id='{self.body_id}', name='{self.name}', source='{self.source}')>"