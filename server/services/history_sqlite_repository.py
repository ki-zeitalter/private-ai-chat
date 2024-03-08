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
                    messages TEXT,
                    timestamp TEXT,
                    app_type TEXT
                )
            """)

    def add_history(self, user_id, thread_id, messages, app_type):
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
                    INSERT INTO history (user_id, thread_id, messages, timestamp, app_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, thread_id, messages_json, datetime.now().isoformat(), app_type))

    def get_history(self, user_id):
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT thread_id, messages, timestamp, app_type
                FROM history
                WHERE user_id = ?
                ORDER BY timestamp DESC
            """, (user_id,))
            rows = cursor.fetchall()
            history = [
                {
                    "thread_id": row[0],
                    "messages": json.loads(row[1]),
                    "timestamp": row[2],
                    "app_type": row[3]
                }
                for row in rows
            ]
            return history

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
