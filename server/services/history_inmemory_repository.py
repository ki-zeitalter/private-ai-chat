from datetime import datetime


class HistoryInMemoryRepository:
    def __init__(self):
        self._history = []

    def add_history(self, user_id, thread_id, messages):
        index_of_existing = self._get_history_index(user_id, thread_id)

        if index_of_existing is not None:
            self._history[index_of_existing]["messages"] = messages
            self._history[index_of_existing]["timestamp"] = datetime.now().isoformat()
        else:
            self._history.append({"user_id": user_id,
                                  "thread_id": thread_id,
                                  "messages": messages,
                                  "timestamp": datetime.now().isoformat()})

    def get_history(self, user_id):
        user_history = [item for item in self._history if item["user_id"] == user_id]
        sorted_history = sorted(user_history, key=lambda x: x['timestamp'], reverse=True)
        return sorted_history

    def get_history_thread(self, user_id, thread_id):
        return [item["messages"] for item in self._history if
                item["user_id"] == user_id and item["thread_id"] == thread_id]

    def _get_history_index(self, user_id, thread_id):
        for index, item in enumerate(self._history):
            if item["user_id"] == user_id and item["thread_id"] == thread_id:
                return index
        return None
