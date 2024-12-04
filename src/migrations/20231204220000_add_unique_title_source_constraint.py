"""Add unique constraint for title and source_id in posts table"""

from sqlalchemy import text
from .base_migration import BaseMigration

class AddUniqueTitleSourceConstraint(BaseMigration):
    """Migration to add unique constraint for title and source_id in posts table"""

    def _execute(self):
        """Execute the migration"""
        # Drop existing index if it exists
        self.db.session.execute(text("""
            DROP INDEX IF EXISTS idx_title_source;
        """))

        # Create unique index
        self.db.session.execute(text("""
            CREATE UNIQUE INDEX idx_title_source
            ON posts(title, source_id);
        """))
        self.db.session.commit()

def run():
    migration = AddUniqueTitleSourceConstraint()
    migration.migrate()

if __name__ == '__main__':
    run()
    