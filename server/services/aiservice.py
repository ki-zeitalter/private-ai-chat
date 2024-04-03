import json

from model.assistant import Assistant


class AIService:

    def __init__(self, history_service, services, assistant_repository):
        self.history_service = history_service
        self.services = services
        self.assistant_repository = assistant_repository

    def chat(self, body, user_id, thread_id):
        # Text messages are stored inside request body using the Deep Chat JSON format:
        # https://deepchat.dev/docs/connect

        # Sends response back to Deep Chat using the Response format:
        # https://deepchat.dev/docs/connect/#Response

        # Save the message to the history
        messages = body["messages"]

        thread_name = self.ensure_thread_name(messages, body, user_id, thread_id)

        self.history_service.add_history(user_id, thread_id, messages, 'chat', thread_name)

        model_service = self.get_provider(body, user_id, thread_id)
        result = model_service.chat(messages)

        messages.append({'role': 'ai', 'text': result['text']})
        self.history_service.add_history(user_id, thread_id, messages, 'chat')

        return result

    def chat_stream(self, body, user_id, thread_id):
        # Save the message to the history
        messages = body["messages"]

        # self.ensure_system_prompt(messages)
        thread_name = self.ensure_thread_name(messages, body, user_id, thread_id)

        self.history_service.add_history(user_id, thread_id, messages, 'chat', thread_name=thread_name)

        def callback(response):
            messages.append({'role': 'ai', 'text': response})
            self.history_service.add_history(user_id, thread_id, messages, 'chat')

        model_service = self.get_provider(body, user_id, thread_id)
        return model_service.chat_stream(messages, callback)

    def ensure_system_prompt(self, messages):
        if not self._system_prompt_included(messages):
            with open('settings/default_chat_system_prompt.txt', 'r') as file:
                system_prompt = file.read()
            messages.insert(0, {'role': 'system', 'text': system_prompt})

    def text_to_image(self, body, user_id, thread_id):
        messages = body["messages"]

        thread_name = self.ensure_thread_name(messages, body, user_id, thread_id)

        image_settings = body.get("imageSettings", {})
        self.history_service.add_history(user_id, thread_id, messages, 'text-to-image', thread_name)

        model_service = self.get_provider(body, user_id, thread_id)
        result = model_service.text_to_image(messages, image_settings)

        messages.append({'role': 'ai', 'files': result['files']})
        self.history_service.add_history(user_id, thread_id, messages, 'text-to-image')

        return result

    def assistant_chat(self, request, user_id, thread_id, assistant_id):
        files = request.files.getlist("files")
        messages = []

        if files:
            text_messages = list(request.form.items())
            if len(text_messages) > 0:
                for key, value in text_messages:
                    messages.append(json.loads(value))
        else:
            messages = request.json["messages"]

        thread_name = self.ensure_thread_name(messages, request, user_id, thread_id)

        self.history_service.add_history(user_id, thread_id, messages, 'analyzer', thread_name=thread_name,
                                         assistant_id=assistant_id)

        assistant = self.assistant_repository.get_assistant(assistant_id)

        # TODO: Errorhandling if assistant is not found
        model_service = self.get_provider(request, user_id, thread_id)
        result = model_service.code_interpreter(messages, files, thread_id, assistant)
        messages.append({'role': 'ai', 'text': result['text']})

        if result.get('files'):
            messages.append({'role': 'ai', 'files': result['files']})

        self.history_service.add_history(user_id, thread_id, messages, 'chat')

        return result

    def create_assistant(self, assistant: Assistant) -> Assistant:
        model_service = self.services.get("openai")  # TODO: currently hardcoded to OpenAI
        created_assistant = model_service.create_assistant(assistant)

        self.assistant_repository.create_assistant(created_assistant)

        return created_assistant

    def _generate_thread_name(self, question, body, user_id, thread_id):
        messages = [
            {'role': 'user',
             'text': f'What is the topic of the following question. Use only up to five words. Answer in the '
                     f'language of the question. The question: {question}'}]

        model_service = self.get_provider(body, user_id, thread_id)
        response = model_service.chat(messages)
        return response['text']

    def _system_prompt_included(self, messages):
        return any(message['role'] == 'system' for message in messages)

    def get_provider(self, body, user_id, thread_id):
        provider = self.determine_provider(body, user_id, thread_id)
        return self.services.get(provider)

    def determine_provider(self, body, user_id, thread_id):
        if self.history_service.is_new_thread(user_id, thread_id):
            return body.get("provider", "openai")
        else:
            return "openai"

    def ensure_thread_name(self, messages, body, user_id, thread_id):
        if self.history_service.is_new_thread(user_id, thread_id):
            user_message = next((message for message in messages if message['role'] == 'user'), None)
            if user_message:
                thread_name = self._generate_thread_name(user_message['text'], body, user_id, thread_id)
                print(thread_name)
                return thread_name
