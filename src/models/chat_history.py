from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from .base import Base

class ChatHistory(Base):
    __tablename__ = 'chat_histories'
    
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    role = Column(String(50))
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    post = relationship("Post", back_populates="chat_histories")
