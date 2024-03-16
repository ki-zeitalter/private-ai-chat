from enum import Enum


class AgentCreator(Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"

    def to_dict(self):
        return self.__dict__


class Agent:
    def __init__(self, agent_id: str, name: str, creator: AgentCreator, instructions: str, tools: list,
                 provider_id: str = None, provider_name: str = None):
        self.agent_id = agent_id
        self.name = name
        self.tools = tools
        self.instructions = instructions
        self.creator = creator
        self.provider_id = provider_id
        self.provider_name = provider_name

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        return (f"Agent(agent_id={self.agent_id}, name={self.name}, creator={self.creator}, "
                f"instructions={self.instructions}, tools={self.tools}, provider_id={self.provider_id}, "
                f"provider_name={self.provider_name})")
