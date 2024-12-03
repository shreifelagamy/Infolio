from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

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

def init_db(db_path='sqlite:///data/content_aggregator.db'):
    engine = create_engine(db_path)
    Base.metadata.create_all(engine)
    return engine
