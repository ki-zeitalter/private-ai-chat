class HistoryInMemoryRepository:
    def __init__(self):
        self._history = []

    def add_history(self, user_id, thread_id, history):
        index_of_existing = self._get_history_index(user_id, thread_id)
        if index_of_existing is not None:
            self._history[index_of_existing]["history"] = history
        else:
            self._history.append({"user_id": user_id, "thread_id": thread_id, "history": history})

    def get_history(self, user_id):
        return [item["history"] for item in self._history if item["user_id"] == user_id]

    def get_history_thread(self, user_id, thread_id):
        return [item["history"] for item in self._history if
                item["user_id"] == user_id and item["thread_id"] == thread_id]

    def _get_history_index(self, user_id, thread_id):
        for index, item in enumerate(self._history):
            if item["user_id"] == user_id and item["thread_id"] == thread_id:
                return index
        return None
