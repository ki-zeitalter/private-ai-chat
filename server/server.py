from requests.exceptions import ConnectionError
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS
import os

from services.aiservice import AIService
from services.history_inmemory_repository import HistoryInMemoryRepository
from services.history_service import HistoryService
from services.history_sqlite_repository import HistorySQLiteRepository
from services.openAIService import OpenAIService

# ------------------ SETUP ------------------

load_dotenv()

app = Flask(__name__)

# this will need to be reconfigured before taking the app to production
cors = CORS(app)

history_repository = HistoryInMemoryRepository()

history_sqlite = HistorySQLiteRepository('history.db')

history_service = HistoryService(history_sqlite)

openai_service = OpenAIService()

ai_service = AIService(history_service, openai_service)


# ------------------ EXCEPTION HANDLERS ------------------

# Sends response back to Deep Chat using the Response format:
# https://deepchat.dev/docs/connect/#Response
@app.errorhandler(Exception)
def handle_exception(e):
    print(e)
    return {"error": str(e)}, 500


@app.errorhandler(ConnectionError)
def handle_exception(e):
    print(e)
    return {"error": "Internal service error"}, 500


@app.route("/chat", methods=["POST"])
def chat():
    body = request.json
    user_id = request.headers.get('User-Id')
    if user_id is None:
        return {"error": "User-Id header is required"}, 400

    thread_id = request.headers.get('Thread-Id')
    if thread_id is None:
        return {"error": "Thread-Id header is required"}, 400

    return ai_service.chat(body, user_id, thread_id)


@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    body = request.json

    user_id = request.headers.get('User-Id')
    if user_id is None:
        return {"error": "User-Id header is required"}, 400

    thread_id = request.headers.get('Thread-Id')
    if thread_id is None:
        return {"error": "Thread-Id header is required"}, 400

    return ai_service.chat_stream(body, user_id, thread_id)


@app.route("/text-to-image", methods=["POST"])
def text_to_image():
    body = request.json
    user_id = request.headers.get('User-Id')
    if user_id is None:
        return {"error": "User-Id header is required"}, 400

    thread_id = request.headers.get('Thread-Id')
    if thread_id is None:
        return {"error": "Thread-Id header is required"}, 400
    return ai_service.text_to_image(body, user_id, thread_id)


@app.route("/files", methods=["POST"])
def files():
    return ai_service.files(request)


@app.route("/interpreter", methods=["GET"])
def interpreter():
    return openai_service.code_interpreter([])

@app.route("/history", methods=["GET"])
def history():
    user_id = request.headers.get('User-Id')
    if user_id is None:
        return {"error": "User-Id header is required"}, 400
    return history_service.get_history(user_id)


# ------------------ START SERVER ------------------

if __name__ == "__main__":
    app.run(port=os.getenv("PORT", 8080), threaded=True, debug=True)
