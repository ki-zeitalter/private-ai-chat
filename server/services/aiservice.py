import json


class AIService:

    def __init__(self, history_service, model_service):
        self.history_service = history_service
        self.model_service = model_service

    def chat(self, body, user_id, thread_id):
        # Text messages are stored inside request body using the Deep Chat JSON format:
        # https://deepchat.dev/docs/connect

        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response

        # Save the message to the history
        messages = body["messages"]

        thread_name = self.ensure_thread_name(messages, user_id, thread_id)

        self.history_service.add_history(user_id, thread_id, messages, 'chat', thread_name)

        result = self.model_service.chat(messages)

        messages.append({'role': 'ai', 'text': result['text']})
        self.history_service.add_history(user_id, thread_id, messages, 'chat')

        return result

    def chat_stream(self, body, user_id, thread_id):
        # Save the message to the history
        messages = body["messages"]

        # self.ensure_system_prompt(messages)
        thread_name = self.ensure_thread_name(messages, user_id, thread_id)

        self.history_service.add_history(user_id, thread_id, messages, 'chat', thread_name=thread_name)

        def callback(response):
            messages.append({'role': 'ai', 'text': response})
            self.history_service.add_history(user_id, thread_id, messages, 'chat')

        return self.model_service.chat_stream(messages, callback)

    def ensure_system_prompt(self, messages):
        if not self._system_prompt_included(messages):
            with open('settings/default_chat_system_prompt.txt', 'r') as file:
                system_prompt = file.read()
            messages.insert(0, {'role': 'system', 'text': system_prompt})

    def text_to_image(self, body, user_id, thread_id):
        messages = body["messages"]

        thread_name = self.ensure_thread_name(messages, user_id, thread_id)

        image_settings = body.get("imageSettings", {})
        self.history_service.add_history(user_id, thread_id, messages, 'text-to-image', thread_name)
        result = self.model_service.text_to_image(messages, image_settings)

        messages.append({'role': 'ai', 'files': result['files']})
        self.history_service.add_history(user_id, thread_id, messages, 'text-to-image')

        return result

    def interpreter(self, request, user_id, thread_id):
        files = request.files.getlist("files")
        messages = []

        if files:
            text_messages = list(request.form.items())
            if len(text_messages) > 0:
                for key, value in text_messages:
                    messages.append(json.loads(value))
        else:
            messages = request.json["messages"]

        print(messages)
        print(files)

        thread_name = self.ensure_thread_name(messages, user_id, thread_id)

        self.history_service.add_history(user_id, thread_id, messages, 'analyzer', thread_name=thread_name)

        result = self.model_service.code_interpreter(messages, files, thread_id)
        messages.append({'role': 'ai', 'text': result['text']})
        self.history_service.add_history(user_id, thread_id, messages, 'chat')

        return result

    def _generate_thread_name(self, question):
        messages = [
            {'role': 'user',
             'text': f'What is the topic of the following question. Use only up to five words. Answer in the '
                     f'language of the question. The question: {question}'}]

        response = self.model_service.chat(messages)
        return response['text']

    def _system_prompt_included(self, messages):
        return any(message['role'] == 'system' for message in messages)

    def ensure_thread_name(self, messages, user_id, thread_id):
        if self.history_service.is_new_thread(user_id, thread_id):
            user_message = next((message for message in messages if message['role'] == 'user'), None)
            if user_message:
                thread_name = self._generate_thread_name(user_message['text'])
                print(thread_name)
                return thread_name
