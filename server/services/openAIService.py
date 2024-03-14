import base64
import json
import os
import queue
import threading
import time
from io import BufferedReader
from typing import Any

import requests
from flask import Response
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.outputs import LLMResult
from langchain_openai import ChatOpenAI
from openai import OpenAI
import sqlite3


# Make sure to set the OPENAI_API_KEY environment variable in a .env file
# (create if it does not exist) - see .env.example

class OpenAIService:
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

    def llm_thread(self, generator, messages, callback):

        try:
            chat = ChatOpenAI(
                model=os.getenv("OPENAI_MODEL", "gpt-4"),
                verbose=True,
                streaming=True,
                callbacks=[ChainStreamHandler(generator, callback)],
                temperature=0,
            )

            chat(messages=messages)
        finally:
            generator.close()

    def chain(self, prompt, callback):
        generator = ThreadedGenerator()
        threading.Thread(target=self.llm_thread, args=(generator, prompt, callback)).start()
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
        return Response(self.chain(self.convert_messages_to_langchain_format(messages), callback),
                        mimetype='text/event-stream')

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

    def code_interpreter(self, messages, files, thread_id):
        client = OpenAI()

        thread_data = self.load_thread_data(thread_id)

        assistant = self.get_assistant()

        if thread_data is not None:
            file_ids = thread_data['file_ids']
        else:
            file_ids = []

        if files:
            for requestFile in files:
                fileReader = BufferedReader(requestFile)
                file = client.files.create(
                    file=(requestFile.filename, fileReader),
                    purpose='assistants'
                )
                file_ids.append(file.id)

        if thread_data is None:
            thread = client.beta.threads.create()
        else:
            thread = client.beta.threads.retrieve(thread_data['thread_id_openai'])

        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=messages[-1]["text"],
            file_ids=file_ids
        )

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        self.store_thread_data(thread_id, file_ids, thread.id, assistant.id)

        existing_messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
        existing_message_ids = [message.id for message in existing_messages]

        while run.status in ['queued', 'in_progress', 'cancelling']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

        if run.status == "completed":

            messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")

            # FIXME: This is a temporary solution to get the response text
            response_text = ""
            generated_file = None
            for message in messages:

                if message.id in existing_message_ids:
                    continue

                for content in message.content:
                    if content.type == "text":
                        if message.role == "assistant":
                            response_text += content.text.value + "\n\n"
                    elif content.type == "image_file":
                        print("Image file")  # MessageContentImageFile

                        image_data = client.files.content(content.image_file.file_id)
                        image_data_bytes = image_data.read()
                        generated_file = base64.b64encode(image_data_bytes).decode()
                    else:
                        print("Other type of message", content.type)
                        print(message.content[0]) # TODO: Handle other types of messages

            if generated_file is not None:
                return {"text": response_text,
                        "files": [{"type": "image", "src": "data:image/png;base64," + generated_file}]}

            return {"text": response_text}
        else:
            print("Status is not completed...", run.status)

        return {'text': 'Something went wrong... sorry!.'}

    def get_assistant(self):
        client = OpenAI()

        assistants = client.beta.assistants.list()

        for assistant in assistants:
            print(assistant.id, assistant.name, assistant.instructions, assistant.model, assistant.tools)
            if assistant.name == "Data Analyst":
                return client.beta.assistants.retrieve(assistant.id)

        assistant = client.beta.assistants.create(
            name="Data Analyst",
            instructions="You are a data analyst. When needed, write and run code "
                         "to answer the question.",
            model="gpt-4-turbo-preview",
            tools=[{"type": "code_interpreter"}],
        )
        return assistant

    def get_connection(self):
        conn = sqlite3.connect('openai_data.db')
        c = conn.cursor()

        c.execute('''
                    CREATE TABLE IF NOT EXISTS ThreadData (
                        thread_id TEXT PRIMARY KEY,
                        file_ids TEXT,
                        thread_id_openai TEXT,
                        assistant_id TEXT
                    )
                ''')
        return conn

    def load_thread_data(self, thread_id):
        conn = self.get_connection()
        c = conn.cursor()

        c.execute('SELECT * FROM ThreadData WHERE thread_id = ?', (thread_id,))
        data = c.fetchone()

        conn.close()

        if data is None:
            return None

        thread_data = {
            'thread_id': data[0],
            'file_ids': data[1].split(','),
            'thread_id_openai': data[2],
            'assistant_id': data[3]
        }

        return thread_data

    def store_thread_data(self, thread_id, file_ids, thread_id_openai, assistant_id):

        conn = self.get_connection()

        c = conn.cursor()
        file_ids_str = ','.join(file_ids)
        c.execute('''
                INSERT OR REPLACE INTO ThreadData (thread_id, file_ids, thread_id_openai, assistant_id)
                VALUES (?, ?, ?, ?)
            ''', (thread_id, file_ids_str, thread_id_openai, assistant_id))
        conn.commit()

        conn.close()


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
    def __init__(self, gen, callback):
        super().__init__()
        self.gen = gen
        self.callback = callback

    def on_llm_new_token(self, token: str, **kwargs):
        self.gen.send("data: {}\n\n".format(json.dumps({"text": token})))

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.callback(response.generations[-1][-1].text)
