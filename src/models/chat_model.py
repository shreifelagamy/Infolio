from typing import List, Dict, Any, Optional
from datetime import datetime
from database.db_connection import DatabaseConnection
from config import DB_PATH

class Chat:
    def __init__(self) -> None:
        self.db = DatabaseConnection(DB_PATH)
        self.create_table()

    def create_table(self) -> None:
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                user_message TEXT NULL,
                assistant_message TEXT,
                generated_post TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES articles(id)
            )
        """)

    def save_chat(self, article_id: int, user_message: Optional[str] = None, assistant_message: Optional[str] = None, generated_post: Optional[str] = None) -> None:
        self.db.execute("""
            INSERT INTO chats (article_id, user_message, assistant_message, generated_post)
            VALUES (?, ?, ?, ?)
        """, (article_id, user_message, assistant_message, generated_post))

    def get_chats_by_article(self, article_id: int) -> List[Dict[str, Any]]:
        rows = self.db.fetch_all("""
            SELECT * FROM chats
            WHERE article_id = ?
        """, (article_id,))
        columns = ["id", "article_id", "user_message", "assistant_message", "generated_post", "created_at"]
        return [dict(zip(columns, row)) for row in rows]

    def clear_chats(self) -> None:
        self.db.execute('DELETE FROM chats')

    def close_conn(self) -> None:
        self.db.close()
