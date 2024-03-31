from abc import ABC, abstractmethod
from typing import List

from model.assistant import Assistant


class AssistantRepository(ABC):

    @abstractmethod
    def get_assistant(self, assistant_id: str) -> Assistant | None:
        pass

    @abstractmethod
    def get_assistants(self) -> List[Assistant]:
        pass

    @abstractmethod
    def create_assistant(self, assistant: Assistant) -> Assistant:
        pass

    @abstractmethod
    def update_assistant(self, assistant: Assistant) -> Assistant:
        pass

    @abstractmethod
    def delete_assistant(self, assistant_id: str) -> None:
        pass

    @abstractmethod
    def get_assistant_by_name(self, assistant_name):
        pass
