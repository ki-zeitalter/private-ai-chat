class File:

    def __init__(self, name: str, content: str, type: str):
        self.name = name
        self.content = content
        self.type = type

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data: dict) -> 'File':
        return cls(
            name=data['name'],
            content=data['content'],
            type=data['type']
        )
