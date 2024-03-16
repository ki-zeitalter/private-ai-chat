from abc import ABC, abstractmethod
from typing import List

from services.agent import Agent


class AgentRepository(ABC):

    @abstractmethod
    def get_agent(self, agent_id: str) -> Agent | None:
        pass

    @abstractmethod
    def get_agents(self) -> List[Agent]:
        pass

    @abstractmethod
    def create_agent(self, agent: Agent) -> Agent:
        pass

    @abstractmethod
    def update_agent(self, agent: Agent) -> Agent:
        pass

    @abstractmethod
    def delete_agent(self, agent_id: str) -> None:
        pass
