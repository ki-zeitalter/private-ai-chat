import json
import os

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from requests.exceptions import ConnectionError

from services.agent import Agent
from services.agent_repository_sqlite import AgentRepositorySqlite
from services.aiservice import AIService
from services.history_service import HistoryService
from services.history_sqlite_repository import HistorySQLiteRepository
from services.openAIService import OpenAIService

# ------------------ SETUP ------------------

load_dotenv()

app = Flask(__name__)

# this will need to be reconfigured before taking the app to production
cors = CORS(app)

# history_repository = HistoryInMemoryRepository()


# ensure_agents_are_predefined(agent_service)

history_sqlite = HistorySQLiteRepository('history.db')

history_service = HistoryService(history_sqlite)

openai_service = OpenAIService()

agent_repository = AgentRepositorySqlite('agents.db')

ai_service = AIService(history_service, openai_service, agent_repository)


# agent_service = AgentService(AgentRepositorySqlite('agents.db'), ai_service)


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


@app.route("/interpreter", methods=["POST"])
def interpreter():
    user_id = request.headers.get('User-Id')
    if user_id is None:
        return {"error": "User-Id header is required"}, 400

    thread_id = request.headers.get('Thread-Id')
    if thread_id is None:
        return {"error": "Thread-Id header is required"}, 400

    assistant_id = request.headers.get('Assistant-Id')
    if assistant_id is None:
        return {"error": "Assistant-Id header is required"}, 400

    result = ai_service.interpreter(request, user_id, thread_id, assistant_id)
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


@app.route("/agents", methods=["GET"])
def get_agents():
    agents = agent_repository.get_agents()
    return jsonify([agent.to_dict() for agent in agents])


@app.route("/agents/", methods=["POST"])
def create_agent():
    agent_data = request.json
    agent = Agent.from_dict(agent_data)
    agent.tools = [json.loads(tool) for tool in agent.tools]
    return jsonify(ai_service.create_agent(agent).to_dict())


@app.route("/agents/<agent_id>", methods=["DELETE"])
def delete_agent(agent_id):
    # TODO: Delete agent in OpenAI
    return agent_repository.delete_agent(agent_id)


# ------------------ START SERVER ------------------

if __name__ == "__main__":
    app.run(port=os.getenv("PORT", 8080), threaded=True, debug=True)
