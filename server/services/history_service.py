from services.history_repository import HistoryRepository


class HistoryService:
    def __init__(self, history_repository: HistoryRepository):
        self.history_repository = history_repository

    def get_history(self, user_id):
        return self.history_repository.get_history(user_id)

    def get_history_thread(self, user_id, thread_id):
        return self.history_repository.get_history_thread(user_id, thread_id)

    def add_history(self, user_id, thread_id, messages, app_type, provider, thread_name=None, assistant_id=None):
        self.history_repository.add_history(user_id, thread_id, messages, app_type, provider, thread_name, assistant_id)

    def is_new_thread(self, user_id, thread_id):
        return self.history_repository.is_new_thread(user_id, thread_id)

    def delete_history(self, thread_id):
        return self.history_repository.delete_thread(thread_id)

