import json
import sqlite3
from datetime import datetime
from services.history_repository import HistoryRepository


class HistorySQLiteRepository(HistoryRepository):
    def __init__(self, db_file):
        self._db_file = db_file
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self._db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    thread_id TEXT,
                    thread_name TEXT,
                    messages TEXT,
                    timestamp TEXT,
                    app_type TEXT,
                    assistant_id TEXT
                )
            """)

    def add_history(self, user_id, thread_id, messages, app_type, thread_name=None, assistant_id=None):
        messages_json = json.dumps(messages)
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM history
                WHERE user_id = ? AND thread_id = ?
            """, (user_id, thread_id))
            result = cursor.fetchone()
            if result:
                history_id = result[0]
                cursor.execute("""
                    UPDATE history
                    SET messages = ?, timestamp = ?
                    WHERE id = ?
                """, (messages_json, datetime.now().isoformat(), history_id))
            else:
                cursor.execute("""
                    INSERT INTO history (user_id, thread_id, thread_name, messages, timestamp, app_type, assistant_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, thread_id, thread_name, messages_json, datetime.now().isoformat(), app_type, assistant_id))

    def get_history(self, user_id):
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT thread_id, thread_name, messages, timestamp, app_type, assistant_id
                FROM history
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, (user_id,))
            rows = cursor.fetchall()
            history = [
                {
                    "thread_id": row[0],
                    "thread_name": row[1],
                    "messages": json.loads(row[2]),
                    "timestamp": row[3],
                    "app_type": row[4],
                    "assistant_id": row[5]
                }
                for row in rows
            ]
            return history

    def delete_thread(self, thread_id):
        conn = sqlite3.connect(self._db_file)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history WHERE thread_id = ?", (thread_id,))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()
        return rows_affected > 0

    def get_history_thread(self, user_id, thread_id):
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT messages
                FROM history
                WHERE user_id = ? AND thread_id = ?
            """, (user_id, thread_id))
            result = cursor.fetchone()
            if result:
                return json.loads(result[0])
            else:
                return None

    def is_new_thread(self, user_id, thread_id):
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM history
                WHERE user_id = ? AND thread_id = ?
            """, (user_id, thread_id))
            return cursor.fetchone() is None
