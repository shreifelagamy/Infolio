from datetime import datetime

from sqlalchemy.exc import IntegrityError

from database import DatabaseManager
from models import Post
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

    def add_posts_from_feed(self, source_id: int, feed_url: str) -> tuple[int, int]:
        """Add posts from a feed URL."""
        try:
            posts = parse_feed(feed_url)
            return self.add_posts_from_feed_entries(source_id, posts)
        except Exception as e:
            return 0, f"Error parsing feed: {str(e)}"

    def add_posts_from_feed_entries(self, source_id: int, entries: list) -> tuple[int, int]:
        """Add posts from feed entries

        Args:
            source_id: ID of the source
            entries: List of feed entries

        Returns:
            tuple: (number of posts added, total number of entries)
        """
        posts_added = 0
        total_entries = len(entries)

        for entry in entries:
            try:
                # Create post object
                post = Post(
                    title=entry.get('title'),
                    description=entry.get('description'),
                    summary=entry.get('summary'),
                    image_url=entry.get('image_url'),
                    external_link=entry.get('link'),
                    published_date=entry.get('published_date'),
                    source_id=source_id
                )

                # Try to add the post
                self.db.session.add(post)
                self.db.session.commit()
                posts_added += 1

            except IntegrityError:
                # Post with this title and source already exists, skip it
                self.db.session.rollback()
                continue

            except Exception as e:
                # Log other errors but continue processing
                print(f"Error adding post: {str(e)}")
                self.db.session.rollback()
                continue

        return posts_added, total_entries
