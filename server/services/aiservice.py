import json

from model.assistant import Assistant


class AIService:

    def __init__(self, history_service, services, assistant_repository):
        self.history_service = history_service
        self.services = services
        self.assistant_repository = assistant_repository

    def chat(self, body, user_id, thread_id):

        # Save the message to the history
        messages = body["messages"]

        thread_name = self.ensure_thread_name(messages, body['provider'], user_id, thread_id)

        provider_id = self.determine_provider(body['provider'], user_id, thread_id)
        self.history_service.add_history(user_id, thread_id, messages, 'chat', provider_id, thread_name)

        model_service = self.get_provider(provider_id, user_id, thread_id)
        result = model_service.chat(messages)

        messages.append({'role': 'ai', 'text': result['text']})
        self.history_service.add_history(user_id, thread_id, messages, 'chat', provider_id)

        return result

    def chat_stream(self, body, user_id, thread_id):
        # Save the message to the history
        messages = body["messages"]

        # self.ensure_system_prompt(messages)
        thread_name = self.ensure_thread_name(messages, body['provider'], user_id, thread_id)
        provider_id = self.determine_provider(body['provider'], user_id, thread_id)
        self.history_service.add_history(user_id, thread_id, messages, 'chat', provider_id, thread_name=thread_name)

        def callback(response):
            messages.append({'role': 'ai', 'text': response})
            self.history_service.add_history(user_id, thread_id, messages, 'chat', provider_id)

        model_service = self.get_provider(provider_id, user_id, thread_id)
        return model_service.chat_stream(messages, callback)

    def ensure_system_prompt(self, messages):
        if not self._system_prompt_included(messages):
            with open('settings/default_chat_system_prompt.txt', 'r') as file:
                system_prompt = file.read()
            messages.insert(0, {'role': 'system', 'text': system_prompt})

    def text_to_image(self, body, user_id, thread_id):
        messages = body["messages"]

        thread_name = self.ensure_thread_name(messages, body['provider'], user_id, thread_id)

        provider_id = self.determine_provider(body['provider'], user_id, thread_id)

        image_settings = body.get("imageSettings", {})
        self.history_service.add_history(user_id, thread_id, messages, 'text-to-image', provider_id, thread_name)

        model_service = self.get_provider(provider_id, user_id, thread_id)
        result = model_service.text_to_image(messages, image_settings)

        messages.append({'role': 'ai', 'files': result['files']})
        self.history_service.add_history(user_id, thread_id, messages, 'text-to-image', provider_id)

        return result

    def assistant_chat(self, request, user_id, thread_id, assistant_id):
        files = request.files.getlist("files")
        messages = []

        if files:
            provider_id_from_request = request.form.get('provider_id')
            text_messages = list(request.form.items())
            if len(text_messages) > 0:
                for key, value in text_messages:
                    if key.startswith("message"):
                        messages.append(json.loads(value))
        else:
            messages = request.json["messages"]
            provider_id_from_request = request.json.get('provider_id')

        # When provider_id_from_request is not set, set it to 'openai'
        if not provider_id_from_request:
            provider_id_from_request = 'openai'

        thread_name = self.ensure_thread_name(messages, provider_id_from_request, user_id, thread_id)

        provider_id = self.determine_provider(provider_id_from_request, user_id, thread_id)

        self.history_service.add_history(user_id, thread_id, messages, 'analyzer', provider_id, thread_name=thread_name,
                                         assistant_id=assistant_id)

        assistant = self.assistant_repository.get_assistant(assistant_id)

        # TODO: Errorhandling if assistant is not found
        model_service = self.get_provider(request, user_id, thread_id)

        def callback(response):
            messages.append({'role': 'ai', 'text': response['text']})
            if response.get('files'):
                messages.append({'role': 'ai', 'files': response['files']})
            self.history_service.add_history(user_id, thread_id, messages, 'chat', provider_id)

        result = model_service.code_interpreter(messages, files, thread_id, assistant, callback)

        return result

    def create_assistant(self, assistant: Assistant) -> Assistant:
        model_service = self.services.get("openai")  # TODO: currently hardcoded to OpenAI
        created_assistant = model_service.create_assistant(assistant)

        self.assistant_repository.create_assistant(created_assistant)

        return created_assistant

    def _generate_thread_name(self, question, provider_id: str, user_id, thread_id):
        messages = [
            {'role': 'user',
             'text': f'What is the topic of the following question. Use only up to five words. Answer in the '
                     f'language of the question. The question: {question}'}]

        model_service = self.get_provider(provider_id, user_id, thread_id)
        response = model_service.chat(messages)
        return response['text']

    def _system_prompt_included(self, messages):
        return any(message['role'] == 'system' for message in messages)

    def get_provider(self, provider_id: str, user_id, thread_id):
        provider = self.determine_provider(provider_id, user_id, thread_id)
        return self.services.get(provider)

    def determine_provider(self, provider_id: str, user_id, thread_id):
        if self.history_service.is_new_thread(user_id, thread_id):
            return provider_id
        else:
            return "openai"  # FIXME: get provider from history

    def ensure_thread_name(self, messages, provider_id: str, user_id, thread_id):
        if self.history_service.is_new_thread(user_id, thread_id):
            user_message = next((message for message in messages if message['role'] == 'user'), None)
            if user_message:
                thread_name = self._generate_thread_name(user_message['text'], provider_id, user_id, thread_id)
                print(thread_name)
                return thread_name
