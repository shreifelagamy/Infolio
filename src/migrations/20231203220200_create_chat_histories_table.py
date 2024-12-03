"""Create chat_histories table migration"""

from sqlalchemy import text
from .base_migration import BaseMigration

class CreateChatHistoriesTable(BaseMigration):
    """Migration to create the chat_histories table"""
    
    def _execute(self):
        """Execute the migration"""
        self.db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS chat_histories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id INTEGER,
                role VARCHAR(50),
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts (id) ON DELETE CASCADE
            )
        """))
        self.db.session.commit()

def run():
    migration = CreateChatHistoriesTable()
    migration.migrate()
    
if __name__ == '__main__':
    run()
