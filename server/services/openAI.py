import queue
import threading

from flask import Response
import requests
import json
import os

from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI


# Make sure to set the OPENAI_API_KEY environment variable in a .env file
# (create if it does not exist) - see .env.example

class OpenAI:
    @staticmethod
    def create_chat_body(messages, stream=False):
        # Text messages are stored inside request body using the Deep Chat JSON format:
        # https://deepchat.dev/docs/connect
        chat_body = {
            "messages": [
                {
                    "role": "assistant" if message["role"] == "ai" else message["role"],
                    "content": message["text"]
                } for message in messages
            ],
            "model": "gpt-4"
        }
        if stream:
            chat_body["stream"] = True
        return chat_body

    @staticmethod
    def create_text_to_image_body(messages, image_settings):
        # Text messages are stored inside request body using the Deep Chat JSON format:
        # https://deepchat.dev/docs/connect
        chat_body = {
            "prompt": messages[-1]["text"],
            "model": image_settings.get("model", "dall-e-3"),
            "n": 1,
            "size": image_settings.get("size", "1024x1024"),
            "quality": image_settings.get("quality", "standard"),
            "style": image_settings.get("style", "vivid"),
            "response_format": "b64_json"
        }

        return chat_body

    def chat(self, messages):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY")
        }
        chat_body = self.create_chat_body(messages)
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", json=chat_body, headers=headers)
        json_response = response.json()
        if "error" in json_response:
            raise Exception(json_response["error"]["message"])
        result = json_response["choices"][0]["message"]["content"]
        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response
        return {"text": result}

    def llm_thread(self, generator, messages):
        try:
            chat = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                verbose=True,
                streaming=True,
                callbacks=[ChainStreamHandler(generator)],
                temperature=0,
            )

            chat(messages=messages)
        finally:
            generator.close()

    def chain(self, prompt):
        generator = ThreadedGenerator()
        threading.Thread(target=self.llm_thread, args=(generator, prompt)).start()
        return generator

    def convert_messages_to_langchain_format(self, messages):
        lc_messages = []
        for message in messages:
            role = message["role"]
            content = message["text"]
            if role == "ai":
                lc_message = AIMessage(content=content)
            else:  # role is "human"
                lc_message = HumanMessage(content=content)
            lc_messages.append(lc_message)
        return lc_messages

    def chat_stream(self, messages, callback):
        return Response(self.chain(self.convert_messages_to_langchain_format(messages)), mimetype='text/event-stream')

    def text_to_image(self, messages, image_settings):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY")
        }
        chat_body = self.create_text_to_image_body(messages, image_settings)

        print(chat_body)

        response = requests.post(
            "https://api.openai.com/v1/images/generations", json=chat_body, headers=headers)
        json_response = response.json()

        print(json_response)

        if "error" in json_response:
            raise Exception(json_response["error"]["message"])

        result = json_response["data"][0]["b64_json"]
        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response
        return {"files": [{"type": "image", "src": "data:image/png;base64," + result}]}

    # By default - the OpenAI API will accept 1024x1024 png images, however other dimensions/formats can sometimes work by default
    # You can use an example image here: https://github.com/OvidijusParsiunas/deep-chat/blob/main/example-servers/ui/assets/example-image.png
    def image_variation(self, files):
        url = "https://api.openai.com/v1/images/variations"
        headers = {
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY")
        }
        # Files are stored inside a files object
        # https://deepchat.dev/docs/connect
        image_file = files[0]
        form = {
            "image": (image_file.filename, image_file.read(), image_file.mimetype)
        }
        response = requests.post(url, files=form, headers=headers)
        json_response = response.json()
        if "error" in json_response:
            raise Exception(json_response["error"]["message"])
        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response
        return {"files": [{"type": "image", "src": json_response["data"][0]["url"]}]}


class ThreadedGenerator:
    def __init__(self):
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item is StopIteration: raise item
        return item

    def send(self, data):
        self.queue.put(data)

    def close(self):
        self.queue.put(StopIteration)


class ChainStreamHandler(StreamingStdOutCallbackHandler):
    def __init__(self, gen):
        super().__init__()
        self.gen = gen

    def on_llm_new_token(self, token: str, **kwargs):
        self.gen.send("data: {}\n\n".format(json.dumps({"text": token})))
