import sqlite3
import os

class FeedManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.feeds = []
        self.init_db()

    def init_db(self):
        db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'feeds.db')
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS feeds
            (id INTEGER PRIMARY KEY, title TEXT, url TEXT UNIQUE)
        ''')
        self.conn.commit()

    def save_feed(self, title, url):
        self.cursor.execute('INSERT OR IGNORE INTO feeds (title, url) VALUES (?, ?)', (title, url))
        self.conn.commit()
        print(f"Saved feed: {title}, {url}")  # Debug print

    def load_feeds(self):
        self.cursor.execute('SELECT title, url FROM feeds')
        self.feeds = self.cursor.fetchall()
        print(f"Loaded feeds: {self.feeds}")  # Debug print
        return self.feeds

    def delete_feed(self, url):
        self.cursor.execute('DELETE FROM feeds WHERE url = ?', (url,))
        self.conn.commit()
        self.feeds = [(title, u) for title, u in self.feeds if u != url]

    def close(self):
        if self.conn:
            self.conn.close()
