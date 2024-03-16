from typing import List

from services.agent import Agent


class AgentService:
    def __init__(self, agent_repository):
        self.agent_repository = agent_repository

    def get_agents(self) -> List[Agent]:
        return self.agent_repository.get_agents()

    def get_agent(self, agent_id) -> Agent | None:
        return self.agent_repository.get_agent(agent_id)

    def create_agent(self, agent) -> Agent:
        return self.agent_repository.create_agent(agent)

    def update_agent(self, agent) -> Agent:
        return self.agent_repository.update_agent(agent)

    def delete_agent(self, agent_id) -> None:
        return self.agent_repository.delete_agent(agent_id)
