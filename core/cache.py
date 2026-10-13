import sqlite3
import json
import os
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "weather_cache.db")

def init_db():
    """Initialize the SQLite caching and community reports database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Weather cache
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_cache (
            city TEXT PRIMARY KEY,
            data TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Mobile Community Emergency Reports
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS community_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            district TEXT NOT NULL,
            province TEXT,
            message TEXT NOT NULL,
            threat_level TEXT DEFAULT 'MODERATE',
            verified INTEGER DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Check if reports table is empty, seed with initial reports
    cursor.execute('SELECT COUNT(*) FROM community_reports')
    count = cursor.fetchone()[0]
    if count == 0:
        initial_reports = [
            ("Saman D.", "Colombo", "Western", "Severe flash flooding starting on Baseline Road near Dematagoda. Heavy traffic congestion, avoid low cars.", "SEVERE", 1),
            ("Nimali P.", "Colombo", "Western", "Power lines down near Borella junction due to intense monsoonal wind gusts. Municipal crew en route.", "MODERATE", 1),
            ("Ruwan K.", "Ratnapura", "Sabaragamuwa", "Continuous heavy rain since 4 AM. Kalu Ganga water level rising near warnings threshold.", "SEVERE", 1),
            ("Dr. Thilak", "Kandy", "Central", "Dense mist on Kadugannawa pass. Visibility under 15 meters. Drive with hazard lights.", "MODERATE", 1),
            ("Chaminda M.", "Galle", "Southern", "Strong rough swells washing over marine drive near Fort. Small boats moved inland.", "MODERATE", 1)
        ]
        cursor.executemany('''
            INSERT INTO community_reports (user_name, district, province, message, threat_level, verified)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', initial_reports)
    
    conn.commit()
    conn.close()

def get_cached_weather(city: str) -> Optional[dict]:
    """Retrieve the last known good weather state for a city/district."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM weather_cache WHERE city = ?', (city.lower(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return None

def set_cached_weather(city: str, data: dict):
    """Store the latest validated weather data into the offline cache."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO weather_cache (city, data, timestamp)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(city) DO UPDATE SET data=excluded.data, timestamp=CURRENT_TIMESTAMP
    ''', (city.lower(), json.dumps(data)))
    conn.commit()
    conn.close()

def add_community_report(user_name: str, district: str, province: str, message: str, threat_level: str = "MODERATE") -> Dict:
    """Inserts a new crowd-sourced mobile disaster report."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO community_reports (user_name, district, province, message, threat_level, verified)
        VALUES (?, ?, ?, ?, ?, 1)
    ''', (user_name.strip(), district.strip(), province.strip() if province else "", message.strip(), threat_level.upper()))
    report_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute('SELECT id, user_name, district, province, message, threat_level, verified, created_at FROM community_reports WHERE id = ?', (report_id,))
    row = cursor.fetchone()
    conn.close()
    
    return {
        "id": row[0],
        "user_name": row[1],
        "district": row[2],
        "province": row[3],
        "message": row[4],
        "threat_level": row[5],
        "verified": bool(row[6]),
        "created_at": row[7]
    }

def get_community_reports(district: Optional[str] = None, limit: int = 15) -> List[Dict]:
    """Retrieves recent crowdsourced emergency reports for mobile feed."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if district:
        cursor.execute('''
            SELECT id, user_name, district, province, message, threat_level, verified, created_at
            FROM community_reports
            WHERE LOWER(district) = LOWER(?)
            ORDER BY id DESC LIMIT ?
        ''', (district.strip(), limit))
    else:
        cursor.execute('''
            SELECT id, user_name, district, province, message, threat_level, verified, created_at
            FROM community_reports
            ORDER BY id DESC LIMIT ?
        ''', (limit,))
        
    rows = cursor.fetchall()
    conn.close()
    
    reports = []
    for r in rows:
        reports.append({
            "id": r[0],
            "user_name": r[1],
            "district": r[2],
            "province": r[3],
            "message": r[4],
            "threat_level": r[5],
            "verified": bool(r[6]),
            "created_at": r[7]
        })
    return reports
