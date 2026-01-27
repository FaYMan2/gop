
import sqlite3
from app.models import Item
from app.constants import DB_PATH

class db_service:
    @staticmethod
    def get_connection():
        """Get a database connection with timeout and WAL mode."""
        conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=10)
        conn.execute('PRAGMA journal_mode=WAL;')
        return conn

    @classmethod
    def init_db(cls):
        """Initialize the database and create tables."""
        with cls.get_connection() as conn:
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

    @classmethod
    def fetch_items(cls):
        """Return all items as a list of dictionaries."""
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT id, device, type, name, content, path, created_at
                FROM items
                ORDER BY created_at DESC
                """
            ).fetchall()
            return [dict(row) for row in rows]

    @classmethod
    def add_item(cls, item: Item):
        """Add an item to the database."""
        with cls.get_connection() as conn:
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

    @classmethod
    def delete_item(cls, item_id: str):
        """Delete an item from the database by ID."""
        with cls.get_connection() as conn:
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

    @classmethod
    def test_db(cls):
        """Test that the database is working."""
        with cls.get_connection() as conn:
            tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print(f"Tables in database: {tables}")
        return tables
    
    @classmethod
    def update_clipboard_item(cls, item: Item):
        """
        Update or create clipboard item.
        Ensures only one clipboard item exists.
        """
        with cls.get_connection() as conn:
            cursor = conn.execute(
                "SELECT id FROM items WHERE type = ? LIMIT 1",
                (item.type.value,)
            )
            row = cursor.fetchone()

            if row:
                conn.execute(
                    """
                    UPDATE items
                    SET content = ?, name = ?, device = ?
                    WHERE id = ?
                    """,
                    (item.content, item.name, item.device, row[0])
                )
            else:
                conn.execute(
                    """
                    INSERT INTO items (id, type, name, content, device)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (item.id, item.type.value, item.name, item.content, item.device)
                )

            conn.commit()

    @classmethod
    def fetch_clipboard_item(cls):
        """Fetch the clipboard item from the db"""
        with cls.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                """
                SELECT id, device, type, name, content, path, created_at
                FROM items
                WHERE type = "clipboard"
                """
            ).fetchall()
            return [dict(row) for row in rows ] if rows else None
            