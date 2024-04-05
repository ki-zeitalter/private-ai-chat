import json
import sqlite3
from typing import List

from model.assistant import Assistant
from model.file import File
from services.assistant_repository import AssistantRepository


class AssistantRepositorySqlite(AssistantRepository):
    def __init__(self, db_file: str):
        self._db_file = db_file
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self._db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS assistant (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    assistant_id TEXT,
                    name TEXT,
                    type TEXT,
                    creator TEXT,
                    instructions TEXT,
                    tools TEXT,
                    provider_id TEXT,
                    provider TEXT,
                    description TEXT,
                    files TEXT
                )
            """)

    def get_assistant(self, assistant_id: str) -> Assistant | None:
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT assistant_id, name, type, creator, instructions, tools, provider_id, provider, 
                description, files
                FROM assistant
                WHERE assistant_id = ?
            """, (assistant_id,))
            row = cursor.fetchone()
            if row:
                return Assistant(assistant_id=row[0],
                                 name=row[1],
                                 type=row[2],
                                 creator=row[3],
                                 instructions=row[4],
                                 tools=json.loads(row[5]),
                                 provider_id=row[6],
                                 provider=row[7],
                                 description=row[8],
                                 files=[File.from_dict(file) for file in json.loads(row[9])])
            return None

    def get_assistants(self) -> List[Assistant]:
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT assistant_id, name, type, creator, instructions, tools, provider_id, provider, 
                description, files
                FROM assistant
            """)
            rows = cursor.fetchall()
            return [Assistant(assistant_id=row[0],
                              name=row[1],
                              type=row[2],
                              creator=row[3],
                              instructions=row[4],
                              tools=json.loads(row[5]),
                              provider_id=row[6],
                              provider=row[7],
                              description=row[8],
                              files=[File.from_dict(file) for file in json.loads(row[9])]) for row in rows]

    def create_assistant(self, assistant: Assistant) -> Assistant:
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO assistant (assistant_id, name, type, creator, instructions, tools, provider_id,
                provider, description, files)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assistant.assistant_id,
                assistant.name,
                assistant.type,
                assistant.creator,
                assistant.instructions,
                json.dumps(assistant.tools),
                assistant.provider_id,
                assistant.provider,
                assistant.description,
                json.dumps([file.to_dict() for file in assistant.files])))
            return assistant

    def update_assistant(self, assistant: Assistant) -> Assistant:
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE assistant
                SET name = ?, type = ?, creator = ?, instructions = ?, tools = ?, provider_id = ?,
                provider = ?, description = ?, files = ?
                WHERE assistant_id = ?
            """, (
                assistant.name,
                assistant.type,
                assistant.creator,
                assistant.instructions,
                json.dumps(assistant.tools),
                assistant.provider_id,
                assistant.provider,
                assistant.description,
                json.dumps([file.to_dict() for file in assistant.files]),
                assistant.assistant_id))
            return assistant

    def delete_assistant(self, assistant_id: str) -> None:
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM assistant
                WHERE assistant_id = ?
            """, (assistant_id,))

    def get_assistant_by_name(self, assistant_name):
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT assistant_id, name, type, creator, instructions, tools, provider_id, provider, 
                description, files
                FROM assistant
                WHERE name = ?
            """, (assistant_name,))
            row = cursor.fetchone()
            if row:
                return Assistant(assistant_id=row[0],
                                 name=row[1],
                                 type=row[2],
                                 creator=row[3],
                                 instructions=row[4],
                                 tools=json.loads(row[5]),
                                 provider_id=row[6],
                                 provider=row[7],
                                 description=row[8],
                                 files=[File.from_dict(file) for file in json.loads(row[9])])
            return None
