from datetime import datetime
from database import DatabaseManager
from services.post_service import PostService
from models.source import Source
from models.post import Post
from typing import List, Tuple

class SourceService:
    def __init__(self, db: DatabaseManager, post_service: PostService):
        self.db = db
        self.post_service = post_service

    def get_all_sources(self) -> List[Source]:
        """Get all active sources."""
        return self.db.session.query(Source).filter(Source.active == True).all()

    def check_source_exists(self, url: str, feed_url: str) -> bool:
        """Check if a source with the given URL or feed URL already exists."""
        return self.db.session.query(Source).filter(
            (Source.url == url) | (Source.feed_url == feed_url)
        ).first() is not None

    def add_source(self, url: str, feed_url: str, name: str = None) -> Tuple[bool, str]:
        """Add a new source and fetch its initial posts."""
        if self.check_source_exists(url, feed_url):
            return False, "Source already exists"

        try:
            source = self.db.add_source(url=url, feed_url=feed_url, name=name)

            if feed_url:
                success, message = self.post_service.add_posts_from_feed(source.id, feed_url)
                if not success:
                    return False, f"Source added but failed to fetch posts: {message}"
                
            return True, "Source added successfully"
        except Exception as e:
            return False, f"Failed to add source: {str(e)}"

    def refresh_source_posts(self, source) -> tuple[bool, str]:
        """Refresh posts for a specific source."""
        if not source.feed_url:
            return False, "No feed URL available for this source"

        try:
            # Delete existing posts
            self.db.delete_posts_by_source(source.id)

            # Fetch and add new posts
            success, message = self.post_service.add_posts_from_feed(source.id, source.feed_url)
            if not success:
                return False, f"Failed to fetch new posts: {message}"

            # Update last checked timestamp
            source.last_checked = datetime.utcnow()
            self.db.session.commit()

            return True, "Posts refreshed successfully"
        except Exception as e:
            return False, f"Error refreshing posts: {str(e)}"

    def delete_source(self, source_id: int) -> bool:
        """Delete a source and all its associated posts

        Args:
            source_id: The ID of the source to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            # First, delete all related posts
            self.db.session.query(Post).filter(Post.source_id == source_id).delete()
            
            # Then delete the source
            source = self.db.session.query(Source).filter(Source.id == source_id).first()
            if source:
                self.db.session.delete(source)
                self.db.session.commit()
                return True
            return False
        except Exception as e:
            print(f"Error deleting source: {str(e)}")
            self.db.session.rollback()
            return False

    def get_all_sources(self) -> List[Source]:
        """Get all sources from the database"""
        return self.db.session.query(Source).all()
