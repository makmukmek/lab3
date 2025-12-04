import sqlite3
import logging
from datetime import datetime
from models import Artwork, ValidationError

class DatabaseError(Exception):
    pass

class DatabaseManager:
    def __init__(self, db_name="art_gallery.db"):
        self.db_name = db_name
        self.setup_database()
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            filename='gallery_activity.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def setup_database(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS artworks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        artist TEXT NOT NULL,
                        year INTEGER NOT NULL,
                        style TEXT NOT NULL,
                        price REAL NOT NULL,
                        created_at TEXT NOT NULL
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Ошибка создания базы данных: {e}")
    
    def add_artwork(self, artwork: Artwork):
        artwork.validate()
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
                cursor.execute('''
                    INSERT INTO artworks (title, artist, year, style, price, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (artwork.title, artwork.artist, artwork.year, artwork.style, 
                      artwork.price, current_time))
                conn.commit()
                
                logging.info(f"Added artwork: {artwork.title} by {artwork.artist}")
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(f"Ошибка добавления произведения: {e}")
    
    def get_all_artworks(self):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, artist, year, style, price, created_at 
                    FROM artworks ORDER BY id DESC
                ''')
                rows = cursor.fetchall()
                return [Artwork(*row) for row in rows]
        except sqlite3.Error as e:
            raise DatabaseError(f"Ошибка получения данных: {e}")
    
    def delete_artwork(self, artwork_id: int):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM artworks WHERE id = ?', (artwork_id,))
                conn.commit()
                logging.info(f"Deleted artwork with ID: {artwork_id}")
        except sqlite3.Error as e:
            raise DatabaseError(f"Ошибка удаления произведения: {e}")
   