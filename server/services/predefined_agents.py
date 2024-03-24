import uuid

from services.agent import Agent



def _check_if_agent_exists(agents, agent_name):
    for agent in agents:
        if agent.name == agent_name:
            return True

    return False


def ensure_agents_are_predefined(agent_service):
    agents = agent_service.get_agents()

    agent_exists = _check_if_agent_exists(agents, "Image Generator")

    if not agent_exists:
        agent_service.create_agent(Agent(
            agent_id=str(uuid.uuid4()),
            name="Image Generator",
            type="image_generator",
            creator="AUTOMATED",
            instructions="",
            tools=[],
            description="Generate images by DALL-E 3"
        ))
