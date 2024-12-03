"""Create sources table migration"""

from sqlalchemy import text
from .base_migration import BaseMigration

class CreateSourcesTable(BaseMigration):
    """Migration to create the sources table"""
    
    def _execute(self):
        """Execute the migration"""
        self.db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url VARCHAR(500) UNIQUE NOT NULL,
                feed_url VARCHAR(500),
                name VARCHAR(200),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_checked TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """))
        self.db.session.commit()

def run():
    migration = CreateSourcesTable()
    migration.migrate()
    
if __name__ == '__main__':
    run()
