from enum import Enum


class Agent:
    def __init__(self, agent_id: str, name: str, type: str, creator: str, instructions: str, tools: list,
                 description: str, provider_id: str = None, provider_name: str = None, ):
        self.agent_id = agent_id
        self.name = name
        self.type = type
        self.tools = tools
        self.description = description
        self.instructions = instructions
        self.creator = creator
        self.provider_id = provider_id
        self.provider_name = provider_name

    def to_dict(self):
        return self.__dict__

    def __repr__(self):
        return f"Agent(agent_id={self.agent_id}, name={self.name}, type={self.type}, creator={self.creator}, " \
               f"instructions={self.instructions}, tools={self.tools}, provider_id={self.provider_id}, " \
               f"provider_name={self.provider_name}, description={self.description})"