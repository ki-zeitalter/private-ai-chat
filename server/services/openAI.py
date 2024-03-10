from flask import Response
import requests
import json
import os


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

    def chat_stream(self, messages, callback):
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv("OPENAI_API_KEY")
        }
        chat_body = self.create_chat_body(messages, stream=True)
        response = requests.post(
            "https://api.openai.com/v1/chat/completions", json=chat_body, headers=headers, stream=True)

        def generate():
            final_answer = ""
            # increase chunk size if getting errors for long messages
            for chunk in response.iter_content(chunk_size=2048):
                if chunk:
                    if not (chunk.decode().strip().startswith("data")):
                        print("Chunk should start with 'data':", chunk.decode())
                        error_message = json.loads(chunk.decode())["error"]["message"]
                        print("Error in the retrieved stream chunk:", error_message)
                        # this exception is not caught, however it signals to the user that there was an error
                        raise Exception(error_message)
                    lines = chunk.decode().split("\n")
                    filtered_lines = list(
                        filter(lambda line: line.strip(), lines))
                    for line in filtered_lines:
                        data = line.replace("data:", "").replace(
                            "[DONE]", "").replace("data: [DONE]", "").strip()
                        if data:
                            try:
                                result = json.loads(data)
                                content = result["choices"][0].get("delta", {}).get("content", "")
                                final_answer += content
                                # Sends response back to Deep Chat using the Response format:
                                # https://deepchat.dev/docs/connect/#Response
                                yield "data: {}\n\n".format(json.dumps({"text": content}))
                            except json.JSONDecodeError:
                                # Incomplete JSON string, continue accumulating lines
                                pass

            callback(final_answer)

        return Response(generate(), mimetype="text/event-stream")

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
