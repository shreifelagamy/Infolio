from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from .base import Base

class LinkedInPost(Base):
    __tablename__ = 'linkedin_posts'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    content = Column(Text)
    status = Column(String(50))
    created_at = Column(DateTime, server_default=func.now())
    published_at = Column(DateTime)
    
    post = relationship("Post", back_populates="linkedin_posts")
