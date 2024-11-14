from typing import List, Dict, Any
from database.db_connection import DatabaseConnection
from config import DB_PATH

class Articles:
    def __init__(self) -> None:
        self.db = DatabaseConnection(DB_PATH)
        self.create_table()

    def create_table(self) -> None:
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL UNIQUE,
                description TEXT NULL,
                url TEXT NULL UNIQUE,
                image_urls TEXT NULL,
                scraped_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source TEXT NULL,
                is_read INTEGER DEFAULT 0,
                is_favorite INTEGER DEFAULT 0
            )
        """)

    def save_article(self, title: str, description: str, url: str,
                    image_urls: str, source: str) -> None:
        self.db.execute("""
            INSERT OR IGNORE INTO articles
            (title, description, url, image_urls, source)
            VALUES (?, ?, ?, ?, ?)
        """, (title, description, url, image_urls, source))

    def toggle_read_status(self, article_id: int) -> None:
        self.db.execute("""
            UPDATE articles
            SET is_read = CASE WHEN is_read = 0 THEN 1 ELSE 0 END
            WHERE id = ?
        """, (article_id,))

    def read(self, article_id: int) -> None:
        self.db.execute("""
            UPDATE articles
            SET is_read = 1
            WHERE id = ?
        """, (article_id,))

    def toggle_favorite_status(self, article_id: int) -> None:
        self.db.execute("""
            UPDATE articles
            SET is_favorite = CASE WHEN is_favorite = 0 THEN 1 ELSE 0 END
            WHERE id = ?
        """, (article_id,))

    def set_favorite(self, article_id: int) -> None:
        self.db.execute("""
            UPDATE articles
            SET is_favorite = 1
            WHERE id = ?
        """, (article_id,))

    @staticmethod
    def _convert_image_urls_to_array(image_urls_str: str) -> List[str]:
        return image_urls_str.split(',') if image_urls_str else []

    def get_articles_as_dicts(self) -> List[Dict[str, Any]]:
        columns = [column[1] for column in
                  self.db.fetch_all('PRAGMA table_info(articles)')]

        records = self.db.fetch_all('SELECT * FROM articles ORDER BY id DESC')

        articles = []
        for record in records:
            article = {}
            for i, column in enumerate(columns):
                value = record[i]
                if column == 'image_urls' and value:
                    value = self._convert_image_urls_to_array(value)
                article[column] = value
            articles.append(article)

        return articles

    def get_total_articles(self) -> int:
        result = self.db.fetch_one('SELECT COUNT(*) FROM articles')
        return result[0] if result else 0

    def get_paginated_articles(self, page: int, per_page: int = 10) -> List[Dict[str, Any]]:
        offset = (page - 1) * per_page
        columns = [column[1] for column in
                  self.db.fetch_all('PRAGMA table_info(articles)')]

        records = self.db.fetch_all(
            'SELECT * FROM articles ORDER BY id DESC LIMIT ? OFFSET ?',
            (per_page, offset)
        )

        articles = []
        for record in records:
            article = {}
            for i, column in enumerate(columns):
                value = record[i]
                if column == 'image_urls' and value:
                    value = self._convert_image_urls_to_array(value)
                article[column] = value
            articles.append(article)

        return articles

    def get_total_filtered_articles(self, filter_read: bool = None) -> int:
        query = 'SELECT COUNT(*) FROM articles'
        params = ()

        if filter_read is not None:
            query += ' WHERE is_read = ?'
            params = (1 if filter_read else 0,)

        result = self.db.fetch_one(query, params)
        return result[0] if result else 0

    def get_filtered_articles(self, page: int, per_page: int = 10, filter_read: bool = None) -> List[Dict[str, Any]]:
        offset = (page - 1) * per_page
        columns = [column[1] for column in self.db.fetch_all('PRAGMA table_info(articles)')]

        query = 'SELECT * FROM articles'
        params = []

        if filter_read is not None:
            query += ' WHERE is_read = ?'
            params.append(1 if filter_read else 0)

        query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
        params.extend([per_page, offset])

        records = self.db.fetch_all(query, tuple(params))

        articles = []
        for record in records:
            article = {}
            for i, column in enumerate(columns):
                value = record[i]
                if column == 'image_urls' and value:
                    value = self._convert_image_urls_to_array(value)
                article[column] = value
            articles.append(article)

        return articles

    def close_conn(self) -> None:
        self.db.close()