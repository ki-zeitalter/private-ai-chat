from flask import Response
import time
import json


class AIService:

    def __init__(self, history_service, model_service):
        self.history_service = history_service
        self.model_service = model_service

    def chat(self, body, user_id, thread_id):
        # Text messages are stored inside request body using the Deep Chat JSON format:
        # https://deepchat.dev/docs/connect
        # print(body)
        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response

        # Save the message to the history
        messages = body["messages"]
        self.history_service.add_history(user_id, thread_id, messages, 'chat')

        result = self.model_service.chat(body)

        messages.append({'role': 'ai', 'text': result['text']})
        self.history_service.add_history(user_id, thread_id, messages, 'chat')

        return result

    def chat_stream(self, body, user_id, thread_id):
        # Text messages are stored inside request body using the Deep Chat JSON format:
        # https://deepchat.dev/docs/connect

        # Save the message to the history
        messages = body["messages"]
        self.history_service.add_history(user_id, thread_id, messages, 'chat')

        def callback(response):
            messages.append({'role': 'ai', 'text': response})
            self.history_service.add_history(user_id, thread_id, messages, 'chat')

        return self.model_service.chat_stream(body, callback)

    def text_to_image(self, body, user_id, thread_id):
        messages = body["messages"]
        image_settings = body.get("imageSettings", {})
        self.history_service.add_history(user_id, thread_id, messages, 'text-to-image')
        result = self.model_service.text_to_image(messages, image_settings)

        messages.append({'role': 'ai', 'files': result['files']})
        self.history_service.add_history(user_id, thread_id, messages, 'text-to-image')

        return result

    def files(self, request):
        # Files are stored inside a files object
        # https://deepchat.dev/docs/connect

        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response
        return {"text": "This is a response from a Flask server. Thankyou for your message!"}
