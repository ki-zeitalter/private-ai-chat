from model.file import File


class Assistant:
    def __init__(self, assistant_id: str, name: str, type: str, creator: str, instructions: str, tools: list,
                 description: str, provider_id: str = None, provider: str = None, files: list = None):
        self.assistant_id = assistant_id
        self.name = name
        self.type = type
        self.tools = tools
        self.description = description
        self.instructions = instructions
        self.creator = creator
        self.provider_id = provider_id
        self.provider = provider
        self.files = files if files is not None else []

    def to_dict(self):
        return {**self.__dict__, 'files': [file.to_dict() for file in self.files]}

    @classmethod
    def from_dict(cls, data: dict) -> 'Assistant':
        files = [File.from_dict(file) for file in data.get('files', [])]
        return cls(
            assistant_id=data['assistant_id'],
            name=data['name'],
            type=data['type'],
            creator=data['creator'],
            instructions=data['instructions'],
            tools=data['tools'],
            provider_id=data.get('provider_id'),
            provider=data.get('provider'),
            description=data['description'],
            files=files
        )
