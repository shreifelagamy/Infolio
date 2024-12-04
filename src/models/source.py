from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from .base import Base

class Source(Base):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    url = Column(String(500), nullable=False)
    feed_url = Column(String(500))
    last_checked = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    # Set up cascade deletion for related posts
    posts = relationship('Post', back_populates='source', cascade='all, delete-orphan', passive_deletes=True)
