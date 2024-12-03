"""Migration runner script"""

import os
import importlib
import sys
import re
from typing import List, Optional

def get_migration_files() -> List[str]:
    """Get all migration files in the migrations directory ordered by datetime prefix"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files = []
    
    for file in os.listdir(current_dir):
        if (file.endswith('.py') and 
            file not in ['__init__.py', 'base_migration.py', 'run_migrations.py'] and
            re.match(r'^\d{14}_', file)):  # Match YYYYMMDDHHMMSS_ prefix
            files.append(file[:-3])  # Remove .py extension
    
    # Sort by datetime prefix
    return sorted(files)

def run_migrations(specific_migration: Optional[str] = None):
    """Run all migrations or a specific one"""
    migration_files = get_migration_files()
    
    if not migration_files:
        print("No migrations found")
        return
        
    if specific_migration:
        if specific_migration not in migration_files:
            print(f"Error: Migration {specific_migration} not found")
            return
        migration_files = [specific_migration]
    
    print(f"Found {len(migration_files)} migrations to run")
    
    for migration_file in migration_files:
        try:
            # Extract migration name for display (remove datetime prefix)
            display_name = migration_file[15:] if len(migration_file) > 15 else migration_file
            
            # Import the migration module
            migration_module = importlib.import_module(f'migrations.{migration_file}')
            
            # Run the migration
            print(f"\nRunning migration: {display_name}")
            migration_module.run()
            
        except Exception as e:
            print(f"Error running migration {display_name}: {str(e)}")
            sys.exit(1)  # Exit on any error

if __name__ == '__main__':
    # Check if a specific migration was requested
    specific_migration = sys.argv[1] if len(sys.argv) > 1 else None
    run_migrations(specific_migration)
