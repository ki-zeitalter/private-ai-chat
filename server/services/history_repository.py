from abc import ABC, abstractmethod

from typing import List, Dict


class HistoryRepository(ABC):
    @abstractmethod
    def add_history(self, user_id: str, thread_id: str, messages: List[Dict], app_type: str, thread_name: str = None):
        """
        Adds a new history to the repository or updates an existing history.
        :param thread_name: The name of the thread.
        :param user_id: The ID of the user.
        :param thread_id: The ID of the thread.
        :param messages: A list of messages in the history.
        :param app_type: The type of the history. Default is "chat".
        """
        pass

    @abstractmethod
    def get_history(self, user_id: str) -> List[Dict]:
        pass

    @abstractmethod
    def get_history_thread(self, user_id: str, thread_id: str) -> List[Dict]:
        pass

    @abstractmethod
    def is_new_thread(self, user_id: str, thread_id: str) -> bool:
        pass
