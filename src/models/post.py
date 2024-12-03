from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    description = Column(Text)
    summary = Column(Text)
    image_url = Column(String(500))
    external_link = Column(String(500), unique=True)
    published_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)
    source_id = Column(Integer, ForeignKey('sources.id'))
    
    source = relationship("Source", back_populates="posts")
    chat_histories = relationship("ChatHistory", back_populates="post", cascade="all, delete-orphan")
    linkedin_posts = relationship("LinkedInPost", back_populates="post", cascade="all, delete-orphan")
