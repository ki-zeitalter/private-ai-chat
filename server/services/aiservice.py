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
        print(body)
        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response

        # Save the message to the history
        messages = body["messages"]
        self.history_service.add_history(user_id, thread_id, messages)

        result = self.model_service.chat(body)

        print(result)
        messages.append({'role': 'ai', 'text': result['text']})
        self.history_service.add_history(user_id, thread_id, messages)

        return result

    def chat_stream(self, body):
        # Text messages are stored inside request body using the Deep Chat JSON format:
        # https://deepchat.dev/docs/connect
        print(body)
        response_chunks = "This is a response from a Flask server. Thank you for your message!".split(
            " ")
        response = Response(self.send_stream(response_chunks), mimetype="text/event-stream")
        response.headers["Content-Type"] = "text/event-stream"
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Connection"] = "keep-alive"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response

    def send_stream(self, response_chunks, chunk_index=0):
        if chunk_index < len(response_chunks):
            chunk = response_chunks[chunk_index]
            yield f"data: {json.dumps({'text': f'{chunk} '})}\n\n"
            time.sleep(0.07)
            yield from self.send_stream(response_chunks, chunk_index + 1)
        else:
            yield ""

    def files(self, request):
        # Files are stored inside a files object
        # https://deepchat.dev/docs/connect
        files = request.files.getlist("files")
        if files:
            print("Files:")
            for file in files:
                print(file.filename)

            # When sending text messages along with files - they are stored inside the data form
            # https://deepchat.dev/docs/connect
            text_messages = list(request.form.items())
            if len(text_messages) > 0:
                print("Text messages:")
                # message objects are stored as strings, and they will need to be parsed (JSON.parse) before processing
                for key, value in text_messages:
                    print(key, value)
        else:
            # When sending text messages without any files - they are stored inside a json
            print("Text messages:")
            print(request.json)

        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response
        return {"text": "This is a response from a Flask server. Thankyou for your message!"}
