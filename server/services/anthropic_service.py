import json
import os
import queue
import threading
from typing import Any

import requests
from flask import Response
from langchain_anthropic import ChatAnthropic
from langchain_community.llms.anthropic import Anthropic
from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.outputs import LLMResult

from model.assistant import Assistant


# Make sure to set the ANTHROPIC_API_KEY environment variable in a .env file
# (create if it does not exist) - see .env.example

class AnthropicService:

    def chat(self, messages):

        chat = ChatAnthropic(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
            verbose=True,
            streaming=False,
            temperature=0,
        )

        response = chat(messages=self.convert_messages_to_langchain_format(messages))

        return {"text": response.content}

    def llm_thread(self, generator, messages, callback):

        try:
            chat = ChatAnthropic(
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229"),
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

        return {"text": "Not implemented yet"}

    def code_interpreter(self, messages, files, thread_id, assistant: Assistant):
        return {'text': 'Not implemented yet'}

    def create_assistant(self, assistant: Assistant) -> Assistant:
        pass


class ThreadedGenerator:
    def __init__(self):
        self.queue = queue.Queue()

    def __iter__(self):
        return self

    def __next__(self):
        item = self.queue.get()
        if item is StopIteration:
            raise item
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
