import sqlite3
from pathlib import Path
from typing import List


class MemoryManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(db_path) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    fact TEXT NOT NULL,
                    category TEXT NOT NULL,
                    source_session TEXT,
                    UNIQUE(user_id, fact)
                )
            """)

    def add(self, user_id: str, fact: str, category: str, session_id: str = "") -> dict | None:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute(
                "INSERT OR IGNORE INTO memories(user_id, fact, category, source_session) VALUES (?, ?, ?, ?)",
                (user_id, fact, category, session_id),
            )
            if cursor.rowcount == 0:
                return None
            memory_id = cursor.lastrowid
        return {"id": memory_id, "user_id": user_id, "fact": fact, "category": category, "source_session": session_id}

    def get(self, user_id: str) -> List[dict]:
        with sqlite3.connect(self.db_path) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                "SELECT id, user_id, fact, category, source_session FROM memories WHERE user_id=? ORDER BY id",
                (user_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def delete(self, memory_id: int, user_id: str) -> bool:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute(
                "DELETE FROM memories WHERE id=? AND user_id=?",
                (memory_id, user_id),
            )
            return cursor.rowcount > 0
