from services.history_repository import HistoryRepository


class HistoryService:
    def __init__(self, history_repository: HistoryRepository):
        self.history_repository = history_repository

    def get_history(self, user_id):
        return self.history_repository.get_history(user_id)

    def add_history(self, user_id, thread_id, messages, app_type):
        self.history_repository.add_history(user_id, thread_id, messages, app_type)

