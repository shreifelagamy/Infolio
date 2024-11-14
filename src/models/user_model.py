import sqlite3

class Users:
    def __init__(self):
        self.conn = sqlite3.connect('articles.db', check_same_thread=False)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                medium_token TEXT
            )
        ''')
        self.conn.commit()

    def add_user(self, username, medium_token=None):
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO users (username, medium_token) VALUES (?, ?)',
                      (username, medium_token))
        self.conn.commit()

    def get_user_token(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT medium_token FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        return result[0] if result else None

    def close_conn(self):
        self.conn.close()
