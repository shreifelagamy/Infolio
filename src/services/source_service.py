from datetime import datetime
from database import DatabaseManager
from services.post_service import PostService

class SourceService:
    def __init__(self, db: DatabaseManager, post_service: PostService):
        self.db = db
        self.post_service = post_service

    def get_all_sources(self):
        """Get all active sources."""
        return self.db.get_all_sources()

    def check_source_exists(self, url: str, feed_url: str = None) -> bool:
        """Check if a source already exists with the given URL or feed URL."""
        return self.db.check_source_exists(url, feed_url)

    def add_source(self, url: str, feed_url: str = None, name: str = None) -> tuple[bool, str]:
        """Add a new source and fetch its initial posts."""
        if self.check_source_exists(url, feed_url):
            return False, "Source already exists"
        
        try:
            source = self.db.add_source(url=url, feed_url=feed_url, name=name)
            
            if feed_url:
                success, message = self.post_service.add_posts_from_feed(source.id, feed_url)
                if not success:
                    return False, message
                return True, "Source added and posts fetched successfully"
            return True, "Source added successfully"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error adding source: {str(e)}"

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
                return False, message
            
            # Update last checked timestamp
            source.last_checked = datetime.utcnow()
            self.db.session.commit()
            
            return True, "Posts refreshed successfully"
        except Exception as e:
            return False, f"Error refreshing posts: {str(e)}"
