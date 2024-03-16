import json
import sqlite3
from typing import List

from services.agent import Agent
from services.agent_repository import AgentRepository


class AgentRepositorySqlite(AgentRepository):
    def __init__(self, db_file: str):
        self._db_file = db_file
        self._create_table()

    def _create_table(self):
        with sqlite3.connect(self._db_file) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    name TEXT,
                    creator TEXT,
                    instructions TEXT,
                    tools TEXT,
                    provider_id TEXT,
                    provider_name TEXT             
                )
            """)

    def get_agent(self, agent_id: str) -> Agent | None:
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT agent_id, name, creator, instructions, tools, provider_id, provider_name
                FROM agent
                WHERE agent_id = ?
            """, (agent_id,))
            row = cursor.fetchone()
            if row:
                return Agent(agent_id=row[0],
                             name=row[1],
                             creator=row[2],
                             instructions=row[3],
                             tools=json.loads(row[4]),
                             provider_id=row[5],
                             provider_name=row[6])
            return None

    def get_agents(self) -> List[Agent]:
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT agent_id, name, creator, instructions, tools, provider_id, provider_name
                FROM agent
            """)
            rows = cursor.fetchall()
            return [Agent(agent_id=row[0],
                          name=row[1],
                          creator=row[2],
                          instructions=row[3],
                          tools=json.loads(row[4]),
                          provider_id=row[5],
                          provider_name=row[6]) for row in rows]

    def create_agent(self, agent: Agent) -> Agent:
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO agent (agent_id, name, creator, instructions, tools, provider_id, provider_name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                agent.agent_id,
                agent.name,
                agent.creator,
                agent.instructions,
                json.dumps(agent.tools),
                agent.provider_id,
                agent.provider_name))
            return agent

    def update_agent(self, agent: Agent) -> Agent:
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE agent
                SET name = ?, creator = ?, instructions = ?, tools = ?, provider_id = ?, provider_name = ?
                WHERE agent_id = ?
            """, (
                agent.name,
                agent.creator,
                agent.instructions,
                json.dumps(agent.tools),
                agent.provider_id,
                agent.provider_name,
                agent.agent_id))
            return agent

    def delete_agent(self, agent_id: str) -> None:
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM agent
                WHERE agent_id = ?
            """, (agent_id,))

    def get_agent_by_name(self, agent_name):
        with sqlite3.connect(self._db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT agent_id, name, creator, instructions, tools, provider_id, provider_name
                FROM agent
                WHERE name = ?
            """, (agent_name,))
            row = cursor.fetchone()
            if row:
                return Agent(agent_id=row[0],
                             name=row[1],
                             creator=row[2],
                             instructions=row[3],
                             tools=json.loads(row[4]),
                             provider_id=row[5],
                             provider_name=row[6])
            return None
