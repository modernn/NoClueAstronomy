from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.sql import func

from api.models.db import Base

class CachedEvent(Base):
    """
    Model for cached astronomical event data.
    
    This model stores cached information about astronomical events
    for celestial bodies, such as oppositions, conjunctions, and moon phases.
    """
    
    __tablename__ = "cached_events"
    
    id = Column(String, primary_key=True, index=True)
    body_id = Column(String, nullable=False, index=True)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    data = Column(JSON, nullable=False)
    last_updated = Column(DateTime, default=func.now(), nullable=False)
    source = Column(String, nullable=False)
    
    def __repr__(self):
        """Return string representation of the model."""
        return f"<CachedEvent(id='{self.id}', body_id='{self.body_id}', source='{self.source}')>"