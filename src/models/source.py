from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Source(Base):
    __tablename__ = 'sources'
    
    id = Column(Integer, primary_key=True)
    url = Column(String(500), unique=True, nullable=False)
    feed_url = Column(String(500))
    name = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_checked = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    posts = relationship("Post", back_populates="source")
