import uuid

from services.agent import Agent, AgentCreator
from services.agent_service import AgentService


def _check_if_agent_exists(agents, agent_name):
    for agent in agents:
        if agent.name == agent_name:
            return True

    return False


def ensure_agents_are_predefined(agent_service: AgentService):
    agents = agent_service.get_agents()
    # First, check if an Agent with the name "Data Analyst" doesn't exist
    agent_exists = _check_if_agent_exists(agents, "Data Analyst")

    if not agent_exists:
        agent_service.create_agent(Agent(
            agent_id=str(uuid.uuid4()),
            name="Data Analyst",
            creator=AgentCreator.AUTOMATED,
            instructions="You are a data analyst. When needed, write and run code "
                         "to answer the question.",
            tools=[{"type": "code_interpreter"}]
        ))
