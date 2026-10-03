import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "weather_cache.db")

def init_db():
    """Initialize the SQLite caching database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_cache (
            city TEXT PRIMARY KEY,
            data TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_cached_weather(city: str) -> dict | None:
    """Retrieve the last known good weather state for a city."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM weather_cache WHERE city = ?', (city.lower(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def set_cached_weather(city: str, data: dict):
    """Store the latest validated weather data into the cache."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Upsert logic (SQLite 3.24+)
    cursor.execute('''
        INSERT INTO weather_cache (city, data, timestamp)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(city) DO UPDATE SET data=excluded.data, timestamp=CURRENT_TIMESTAMP
    ''', (city.lower(), json.dumps(data)))
    conn.commit()
    conn.close()
