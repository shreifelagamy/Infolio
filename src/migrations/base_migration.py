"""Base migration class with tracking functionality"""

from sqlalchemy import text
from database import DatabaseManager
from models.migration import Migration

class BaseMigration:
    """Base class for all migrations"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.migration_name = self.__class__.__name__
        
    def _create_migrations_table(self):
        """Create migrations table if it doesn't exist"""
        self.db.session.execute(text("""
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) UNIQUE NOT NULL,
                executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT 1
            )
        """))
        self.db.session.commit()
        
    def _is_migration_executed(self) -> bool:
        """Check if migration was already executed"""
        self._create_migrations_table()
        result = self.db.session.query(Migration)\
            .filter(Migration.name == self.migration_name)\
            .first()
        return result is not None
        
    def _mark_migration_executed(self, success: bool = True):
        """Mark migration as executed"""
        migration = Migration(
            name=self.migration_name,
            success=success
        )
        self.db.session.add(migration)
        self.db.session.commit()
        
    def migrate(self):
        """Execute migration if not already executed"""
        if self._is_migration_executed():
            print(f"Migration {self.migration_name} already executed")
            return
            
        try:
            print(f"Executing migration {self.migration_name}...")
            self._execute()
            self._mark_migration_executed(success=True)
            print(f"Migration {self.migration_name} completed successfully")
        except Exception as e:
            self._mark_migration_executed(success=False)
            print(f"Migration {self.migration_name} failed: {str(e)}")
            raise
            
    def _execute(self):
        """Override this method in concrete migration classes"""
        raise NotImplementedError("Concrete migration classes must implement _execute()")
