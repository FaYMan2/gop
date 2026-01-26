import sqlite3
import uuid
import platform
from pathlib import Path

# Cross-platform database path
if platform.system() == "Windows":
    import os
    BASE = Path(os.environ.get("APPDATA", Path.home())) / "localsync"
else:
    # macOS and Linux
    BASE = Path.home() / ".localsync"

BASE.mkdir(exist_ok=True)
DB_PATH = BASE / "sync.db"


def get_connection():
    """Get a database connection."""
    return sqlite3.connect(str(DB_PATH), check_same_thread=False)


def init_db():
    """Initialize the database and create tables."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            device TEXT NOT NULL,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            content TEXT,
            path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print(f"Database initialized at: {DB_PATH}")

def test_db():
    """Test that the database is working."""
    conn = get_connection()
    rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    conn.close()
    print(f"Tables in database: {rows}")
    return rows
