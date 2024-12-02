from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
from typing import List, Optional

from models import Source, Post, init_db

class DatabaseManager:
    def __init__(self, db_path='sqlite:///data/content_aggregator.db'):
        self.engine = init_db(db_path)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_source(self, url: str, feed_url: Optional[str] = None, name: Optional[str] = None) -> Source:
        """Add a new source to the database."""
        source = Source(
            url=url,
            feed_url=feed_url,
            name=name,
            created_at=datetime.utcnow(),
            last_checked=datetime.utcnow()
        )
        self.session.add(source)
        self.session.commit()
        return source

    def get_all_sources(self) -> List[Source]:
        """Get all sources from the database."""
        return self.session.query(Source).filter_by(is_active=True).all()

    def update_source_feed(self, source_id: int, feed_url: str):
        """Update the feed URL for a source."""
        source = self.session.query(Source).filter_by(id=source_id).first()
        if source:
            source.feed_url = feed_url
            source.last_checked = datetime.utcnow()
            self.session.commit()

    def add_post(self, source_id: int, title: str, description: str, summary: str,
                image_url: Optional[str], external_link: str,
                published_date: Optional[datetime] = None) -> Post:
        """Add a new post to the database."""
        post = Post(
            title=title,
            description=description,
            summary=summary,
            image_url=image_url,
            external_link=external_link,
            published_date=published_date or datetime.utcnow(),
            source_id=source_id
        )
        self.session.add(post)
        self.session.commit()
        return post

    def get_all_posts(self, limit: int = 100) -> List[Post]:
        """Get all posts from the database, ordered by published date."""
        return self.session.query(Post)\
            .order_by(Post.published_date.desc())\
            .limit(limit)\
            .all()

    def get_posts_by_source(self, source_id: int, limit: int = 50) -> List[Post]:
        """Get posts from a specific source."""
        return self.session.query(Post)\
            .filter_by(source_id=source_id)\
            .order_by(Post.published_date.desc())\
            .limit(limit)\
            .all()

    def delete_posts_by_source(self, source_id: int):
        """Delete all posts from a specific source."""
        self.session.query(Post).filter_by(source_id=source_id).delete()
        self.session.commit()

    def close(self):
        """Close the database session."""
        self.session.close()
