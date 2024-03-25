class Assistant:
    def __init__(self, assistant_id: str, name: str, type: str, creator: str, instructions: str, tools: list,
                 description: str, provider_id: str = None, provider_name: str = None, ):
        self.assistant_id = assistant_id
        self.name = name
        self.type = type
        self.tools = tools
        self.description = description
        self.instructions = instructions
        self.creator = creator
        self.provider_id = provider_id
        self.provider_name = provider_name

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict) -> 'Assistant':
        return cls(
            assistant_id=data['assistant_id'],
            name=data['name'],
            type=data['type'],
            creator=data['creator'],
            instructions=data['instructions'],
            tools=data['tools'],
            provider_id=data.get('provider_id'),
            provider_name=data.get('provider_name'),
            description=data['description']
        )

    def __repr__(self):
        return f"Assistant(assistant_id={self.assistant_id}, name={self.name}, type={self.type}, creator={self.creator}, " \
               f"instructions={self.instructions}, tools={self.tools}, provider_id={self.provider_id}, " \
               f"provider_name={self.provider_name}, description={self.description})"
