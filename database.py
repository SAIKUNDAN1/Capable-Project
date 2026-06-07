import sqlite3
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "search_history.db")

def init_db():
    """Initializes the database and creates the history table if it doesn't exist."""
    conn = sqlite3.connect(DB_FILE)
    conn.text_factory = str
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            search_query TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def save_search(session_id: str, query: str):
    """Saves a user search query to the database securely."""
    init_db()
    if not query or not query.strip():
        return
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.text_factory = str
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO search_history (session_id, search_query, timestamp) VALUES (?, ?, ?)",
            (session_id, query.strip(), now)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass

def get_search_history(session_id: str, limit: int = 10):
    """Retrieves the most recent search history for a session."""
    init_db()
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute(
            "SELECT search_query, timestamp FROM search_history WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []
