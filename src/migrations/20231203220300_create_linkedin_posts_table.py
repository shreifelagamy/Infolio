"""Create linkedin_posts table migration"""

from sqlalchemy import text
from .base_migration import BaseMigration

class CreateLinkedInPostsTable(BaseMigration):
    """Migration to create the linkedin_posts table"""
    
    def _execute(self):
        """Execute the migration"""
        self.db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS linkedin_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                content TEXT,
                status VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
            )
        """))
        self.db.session.commit()

def run():
    migration = CreateLinkedInPostsTable()
    migration.migrate()
    
if __name__ == '__main__':
    run()
