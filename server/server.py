import json
import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from requests.exceptions import ConnectionError

from services.assistant import Assistant
from services.assistant_repository_sqlite import AssistantRepositorySqlite
from services.aiservice import AIService
from services.history_service import HistoryService
from services.history_sqlite_repository import HistorySQLiteRepository
from services.openAIService import OpenAIService
from services.predefined_assistants import ensure_assistants_are_predefined

# ------------------ SETUP ------------------

load_dotenv()

app = Flask(__name__)

# this will need to be reconfigured before taking the app to production
cors = CORS(app)

# history_repository = HistoryInMemoryRepository()


history_sqlite = HistorySQLiteRepository('history.db')

history_service = HistoryService(history_sqlite)

openai_service = OpenAIService()

assistant_repository = AssistantRepositorySqlite('assistants.db')

ensure_assistants_are_predefined(assistant_repository)

ai_service = AIService(history_service, openai_service, assistant_repository)


# assistant_service = AssistantService(AssistantRepositorySqlite('assistants.db'), ai_service)


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


@app.route("/assistant-chat", methods=["POST"])
def assistant_chat():
    user_id = request.headers.get('User-Id')
    if user_id is None:
        return {"error": "User-Id header is required"}, 400

    thread_id = request.headers.get('Thread-Id')
    if thread_id is None:
        return {"error": "Thread-Id header is required"}, 400

    assistant_id = request.headers.get('Assistant-Id')
    if assistant_id is None:
        return {"error": "Assistant-Id header is required"}, 400

    result = ai_service.assistant_chat(request, user_id, thread_id, assistant_id)
    return result


@app.route("/history", methods=["GET"])
def history():
    user_id = request.headers.get('User-Id')
    if user_id is None:
        return {"error": "User-Id header is required"}, 400
    return history_service.get_history(user_id)


@app.route("/history/<thread_id>", methods=["DELETE"])
def delete_history(thread_id):
    result = history_service.delete_history(thread_id)
    if result:
        return {"message": "History entry deleted successfully"}, 200
    else:
        return {"error": "History entry not found"}, 404


@app.route("/assistants", methods=["GET"])
def get_assistants():
    assistants = assistant_repository.get_assistants()
    return jsonify([assistant.to_dict() for assistant in assistants])


@app.route("/assistants/", methods=["POST"])
def create_assistant():
    assistant_data = request.json
    assistant = Assistant.from_dict(assistant_data)
    assistant.tools = [json.loads(tool) for tool in assistant.tools]
    return jsonify(ai_service.create_assistant(assistant).to_dict())


@app.route("/assistants/<assistant_id>", methods=["DELETE"])
def delete_assistant(assistant_id):
    # TODO: Delete assistant in OpenAI
    return assistant_repository.delete_assistant(assistant_id)


# ------------------ START SERVER ------------------

if __name__ == "__main__":
    app.run(port=os.getenv("PORT", 8080), threaded=True, debug=True)
