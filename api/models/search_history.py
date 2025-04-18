from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from api.models.db import Base

class SearchHistory(Base):
    """
    Model for search history records.
    
    This model stores search queries for analytics purposes and
    to provide search history functionality to users.
    """
    
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    query = Column(String, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
    source = Column(String, nullable=False)
    
    def __repr__(self):
        """Return string representation of the model."""
        return f"<SearchHistory(id={self.id}, query='{self.query}', source='{self.source}')>"