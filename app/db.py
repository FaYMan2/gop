import sqlite3
from app.models import Item
from app.constants import DB_PATH

def get_connection():
    """Get a database connection with timeout and WAL mode."""
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=10)
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn


def init_db():
    """Initialize the database and create tables."""
    with get_connection() as conn:
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
    print(f"Database initialized at: {DB_PATH}")


def fetch_items():
    """Return all items as a list of dictionaries."""
    with get_connection() as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, device, type, name, content, path, created_at
            FROM items
            ORDER BY created_at DESC
            """
        ).fetchall()
        return [dict(row) for row in rows]

def add_item(item : Item):
    """Add an item to the database."""
    with get_connection() as conn:
        print(item.content)
        conn.execute(
            """
            INSERT INTO items (id, device, type, name, content, path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.id,
                item.device,
                item.type.value,
                item.name,
                item.content,
                item.path,
                item.created_at,
            )
        )
        conn.commit()
    print(f"Item added with ID: {item.id}")
    return {"status": "success", "id": item.id}

def delete_item(item_id: str):
    """Delete an item from the database by ID."""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM items WHERE id = ?",
            (item_id,)
        )
        conn.commit()
        affected_rows = cursor.rowcount
    if affected_rows == 0:
        print(f"No item found with ID: {item_id}")
        return {"status": "error", "message": "Item not found"}
    print(f"Item deleted with ID: {item_id}")
    return {"status": "success", "id": item_id}

def test_db():
    """Test that the database is working."""
    with get_connection() as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print(f"Tables in database: {tables}")
    return tables