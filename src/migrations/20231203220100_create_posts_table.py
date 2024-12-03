"""Create posts table migration"""

from sqlalchemy import text
from .base_migration import BaseMigration

class CreatePostsTable(BaseMigration):
    """Migration to create the posts table"""
    
    def _execute(self):
        """Execute the migration"""
        self.db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(500),
                description TEXT,
                summary TEXT,
                image_url VARCHAR(500),
                external_link VARCHAR(500) UNIQUE,
                published_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_read BOOLEAN DEFAULT 0,
                read_at TIMESTAMP,
                source_id INTEGER,
                FOREIGN KEY (source_id) REFERENCES sources (id)
            )
        """))
        self.db.session.commit()

def run():
    migration = CreatePostsTable()
    migration.migrate()
    
if __name__ == '__main__':
    run()
