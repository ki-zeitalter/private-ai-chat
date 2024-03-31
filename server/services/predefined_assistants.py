import uuid

from model.assistant import Assistant


def _check_if_assistant_exists(assistants, assistant_name):
    for assistant in assistants:
        if assistant.name == assistant_name:
            return True

    return False


def ensure_assistants_are_predefined(assistant_service):
    assistants = assistant_service.get_assistants()

    assistant_exists = _check_if_assistant_exists(assistants, "Image Generator")

    if not assistant_exists:
        assistant_service.create_assistant(Assistant(
            assistant_id=str(uuid.uuid4()),
            name="Image Generator",
            type="image_generator",
            creator="AUTOMATED",
            instructions="",
            tools=[],
            description="Generate images by DALL-E 3"
        ))
