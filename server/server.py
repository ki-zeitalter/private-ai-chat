from requests.exceptions import ConnectionError
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS
import os

from services.aiservice import AIService

# ------------------ SETUP ------------------

load_dotenv()

app = Flask(__name__)

# this will need to be reconfigured before taking the app to production
cors = CORS(app)


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


ai_service = AIService()


@app.route("/chat", methods=["POST"])
def chat():
    body = request.json
    return ai_service.chat(body)


@app.route("/chat-stream", methods=["POST"])
def chat_stream():
    body = request.json
    return ai_service.chat_stream(body)


@app.route("/files", methods=["POST"])
def files():
    return ai_service.files(request)


# ------------------ START SERVER ------------------

if __name__ == "__main__":
    app.run(port=os.getenv("PORT", 8080))
