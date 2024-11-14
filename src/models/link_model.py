from typing import List, Tuple
from datetime import datetime
from database.db_connection import DatabaseConnection
from config import DB_PATH

class Links:
    def __init__(self) -> None:
        self.db = DatabaseConnection(DB_PATH)
        self.create_table()

    def create_table(self) -> None:
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                link TEXT NOT NULL UNIQUE,
                rss_link TEXT UNIQUE,
                last_scrapped_at DATETIME
            )
        """)

    def save_link(self, link: str, rss_link: str = None) -> None:
        self.db.execute(
            "INSERT OR IGNORE INTO links (link, rss_link, last_scrapped_at) VALUES (?, ?, NULL)",
            (link, rss_link)
        )

    def update_last_scrapped(self, link: str) -> None:
        self.db.execute(
            "UPDATE links SET last_scrapped_at = ? WHERE link = ?",
            (datetime.now(), link)
        )

    def get_all_links(self) -> List[Tuple[str, str, datetime]]:
        return self.db.fetch_all('SELECT link, rss_link, last_scrapped_at FROM links')

    def clear_links(self) -> None:
        self.db.execute('DELETE FROM "links"')

    def close_conn(self) -> None:
        self.db.close()