import json, sqlite3
from pathlib import Path

DB_PATH = Path("monitor_state.db")

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS detected_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

def is_new_link(url: str) -> bool:
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT 1 FROM detected_links WHERE url = ?", (url,)).fetchone()
        return row is None

def save_link(url: str, title: str):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO detected_links (url, title) VALUES (?, ?)",
            (url, title)
        )

def get_history():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT url, title, detected_at FROM detected_links ORDER BY detected_at DESC"
        ).fetchall()
        return [{"url": r[0], "title": r[1], "detected_at": r[2]} for r in rows]