import base64
import json
import os
import queue
import sqlite3
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

from model.assistant import Assistant


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

        response = requests.post(
            "https://api.openai.com/v1/images/generations", json=chat_body, headers=headers)
        json_response = response.json()

        if "error" in json_response:
            raise Exception(json_response["error"]["message"])

        result = json_response["data"][0]["b64_json"]
        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response
        return {"files": [{"type": "image", "src": "data:image/png;base64," + result}]}

    def code_interpreter(self, messages, files, thread_id, assistant: Assistant, history_callback):
        return Response(self._code_interpreter(messages, files, thread_id, assistant, history_callback),
                        mimetype='text/event-stream')

    def _code_interpreter(self, messages, files, thread_id, assistant: Assistant, history_callback):
        client = OpenAI()

        thread_data = self.load_thread_data(thread_id)

        openai_assistant = self.get_assistant(assistant)

        if thread_data is not None:
            file_ids = [file_id for file_id in thread_data['file_ids'] if file_id != '']
        else:
            file_ids = []

        if files:
            for requestFile in files:
                file_reader = BufferedReader(requestFile)
                file = client.files.create(
                    file=(requestFile.filename, file_reader),
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

        self.store_thread_data(thread_id, file_ids, thread.id, openai_assistant.id)

        existing_messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")
        existing_message_ids = [message.id for message in existing_messages]

        # Run the assistant asynchronously
        generator = ThreadedGenerator()

        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=openai_assistant.id,
        )

        threading.Thread(target=self.generate_assistant_response,
                         args=(client, existing_message_ids, generator, run, thread, history_callback)).start()
        # self.generate_assistant_response(client, existing_message_ids, generator, run, thread)
        return generator

    def generate_assistant_response(self, client, existing_message_ids, generator, run, thread, history_callback):
        while run.status in ['queued', 'in_progress', 'cancelling', 'completed']:
            time.sleep(1)
            run = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            messages = client.beta.threads.messages.list(thread_id=thread.id, order="asc")

            generated_file = []
            for message in messages:

                if message.id in existing_message_ids:
                    continue

                print(message)

                for content in message.content:
                    response_text = ""
                    if content.type == "text":
                        if message.role == "assistant":
                            response_text += content.text.value + "\n\n"

                            if content.text.annotations:
                                # print("Annotations", content.text.annotations)

                                for annotation in content.text.annotations:
                                    if hasattr(annotation, 'file_path'):
                                        file_data = client.files.content(annotation.file_path.file_id)
                                        file_data_bytes = file_data.read()
                                        b64_content = base64.b64encode(file_data_bytes).decode()
                                        file_name = os.path.basename(annotation.text)
                                        mimetype = "application/octet-stream"

                                        link = "data:" + mimetype + ";name=" + file_name + ";base64," + b64_content
                                        response_text = response_text.replace(annotation.text, link)

                        generator.send("data: {}\n\n".format(
                            json.dumps({"text": response_text})))

                        history_callback({"text": response_text})

                        existing_message_ids.append(message.id)
                    elif content.type == "image_file":
                        print("Image file")  # MessageContentImageFile

                        image_data = client.files.content(content.image_file.file_id)
                        image_data_bytes = image_data.read()
                        b64_content = base64.b64encode(image_data_bytes).decode()
                        generated_file.append({"type": "image", "src": "data:image/png;base64," + b64_content})

                        generator.send("data: {}\n\n".format(
                            json.dumps({"text": response_text, "files": [file for file in generated_file]})))

                        history_callback({"text": response_text, "files": [file for file in generated_file]})

                        existing_message_ids.append(message.id)
                    else:
                        print("Other type of message", content.type)
                        print(message.content[0])  # TODO: Handle other types of messages

                # if generated_file is not None:
                #    return {"text": response_text,
                #            "files": [file for file in generated_file]}

            if run.status == "completed":
                generator.close()
                break

    def create_assistant(self, assistant: Assistant) -> Assistant:
        client = OpenAI()

        file_ids = []
        if assistant.files:
            for requestFile in assistant.files:
                file_content_bytes = base64.b64decode(requestFile.content)
                file = client.files.create(
                    file=(requestFile.name, file_content_bytes),
                    purpose='assistants'
                )
                file_ids.append(file.id)

        openai_assistant = client.beta.assistants.create(
            name=assistant.name,
            instructions=assistant.instructions,
            model="gpt-4-turbo-preview",  # TODO: Get model from assistant
            tools=assistant.tools,
            file_ids=file_ids
        )

        assistant.provider_id = openai_assistant.id
        assistant.provider_name = "openai"

        return assistant

    def get_assistant(self, assistant: Assistant):
        client = OpenAI()

        assistants = client.beta.assistants.list()

        for openai_assistant in assistants:
            print(openai_assistant.id, assistant.name, assistant.instructions, openai_assistant.model, assistant.tools)
            if openai_assistant.id == assistant.provider_id:
                return client.beta.assistants.retrieve(openai_assistant.id)

        return None

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
