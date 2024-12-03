from datetime import datetime
from sqlalchemy.orm import Session
from models import Post, LinkedInPost, ChatHistory
from crews.linkedin import LinkedInCrew
from database import DatabaseManager

class LinkedInService:
    """Service for handling LinkedIn post generation and management"""
    
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.crew = LinkedInCrew()
        
    def generate_linkedin_post(self, post: Post, preferences: dict) -> str:
        """Generate a LinkedIn post for the given article"""
        
        # Record the start of interaction
        self.save_chat_history(post.id, 'system', 'Starting LinkedIn post generation')
        
        # Generate post using CrewAI
        content = post.description or post.summary
        result = self.crew.generate_post(
            title=post.title,
            content=content,
            preferences=preferences
        )
        
        # Save the generated post
        linkedin_post = LinkedInPost(
            post_id=post.id,
            content=result,
            status="draft"
        )
        self.db.session.add(linkedin_post)
        self.db.session.commit()
        
        # Save the final result
        self.save_chat_history(post.id, 'assistant', result)
        
        return result
        
    def get_post_history(self, post_id: int) -> list[ChatHistory]:
        """Get chat history for a post"""
        return self.db.session.query(ChatHistory)\
            .filter(ChatHistory.post_id == post_id)\
            .order_by(ChatHistory.created_at.desc())\
            .all()
            
    def save_chat_history(self, post_id: int, role: str, content: str):
        """Save a chat message to history"""
        history = ChatHistory(
            post_id=post_id,
            role=role,
            content=content
        )
        self.db.session.add(history)
        self.db.session.commit()
        
    def get_linkedin_posts(self, post_id: int) -> list[LinkedInPost]:
        """Get LinkedIn posts for an article"""
        return self.db.session.query(LinkedInPost)\
            .filter(LinkedInPost.post_id == post_id)\
            .order_by(LinkedInPost.created_at.desc())\
            .all()
            
    def update_linkedin_post(self, linkedin_post_id: int, content: str) -> LinkedInPost:
        """Update a LinkedIn post"""
        linkedin_post = self.db.session.query(LinkedInPost)\
            .filter(LinkedInPost.id == linkedin_post_id).first()
        if linkedin_post:
            linkedin_post.content = content
            linkedin_post.status = 'draft'
            self.db.session.commit()
        return linkedin_post
        
    def publish_linkedin_post(self, linkedin_post_id: int) -> LinkedInPost:
        """Publish a LinkedIn post"""
        linkedin_post = self.db.session.query(LinkedInPost)\
            .filter(LinkedInPost.id == linkedin_post_id).first()
        if linkedin_post:
            linkedin_post.status = 'published'
            linkedin_post.published_at = datetime.utcnow()
            self.db.session.commit()
        return linkedin_post
