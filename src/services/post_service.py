from datetime import datetime
from database import DatabaseManager
from utils.feed_utils import parse_feed

class PostService:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_posts(self, limit: int = 10, offset: int = 0):
        """Get paginated posts ordered by published date."""
        return self.db.get_all_posts(limit=limit, offset=offset)

    def get_total_posts_count(self) -> int:
        """Get total number of posts."""
        return self.db.get_total_posts_count()

    def mark_post_as_read(self, post_id: int):
        """Mark a post as read."""
        self.db.mark_post_as_read(post_id)

    def add_posts_from_feed(self, source_id: int, feed_url: str) -> tuple[bool, str]:
        """Add posts from a feed URL."""
        try:
            posts = parse_feed(feed_url)
            for post in posts:
                try:
                    self.db.add_post(
                        source_id=source_id,
                        title=post['title'],
                        description=post.get('description', ''),
                        summary=post.get('summary', ''),
                        image_url=post.get('image_url'),
                        external_link=post['link'],
                        published_date=post['published_date']
                    )
                except Exception as e:
                    return False, f"Error adding post: {str(e)}"
            return True, "Posts added successfully"
        except Exception as e:
            return False, f"Error parsing feed: {str(e)}"
