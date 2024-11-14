import sqlite3
from typing import List, Tuple, Any

class DatabaseConnection:
    def __init__(self, db_name: str) -> None:
        self.db_name = db_name
        self.con = sqlite3.connect(db_name)
        self.cursor = self.con.cursor()

    def execute(self, query: str, params: Tuple[Any, ...] = ()) -> None:
        self.cursor.execute(query, params)
        self.con.commit()

    def fetch_all(self, query: str, params: Tuple[Any, ...] = ()) -> List[Tuple]:
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fetch_one(self, query: str, parameters: tuple = ()) -> tuple:
        """
        Fetch a single row from the database.

        Args:
            query: SQL query string
            parameters: Query parameters (optional)

        Returns:
            Single row as tuple or None if no results
        """
        cursor = self.con.cursor()
        cursor.execute(query, parameters)
        result = cursor.fetchone()
        cursor.close()
        return result

    def close(self) -> None:
        self.con.close()