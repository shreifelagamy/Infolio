"""Migration model to track executed migrations"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from database import Base

class Migration(Base):
    __tablename__ = 'migrations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    executed_at = Column(DateTime, server_default=func.now())
    success = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Migration {self.name} executed_at={self.executed_at}>"
