from time import time


class TemplateMetadata:
    def __init__(self, version: str, last_modified: time, author: str, description: str, template_type: str):
        self.version = version
        self.last_modified = last_modified
        self.author = author
        self.description = description
        self.template_type = template_type


class Template:
    def __init__(self, id: str, name: str, content: str, metadata: TemplateMetadata, builtin=False):
        self.id = id
        self.name = name
        self.content = content
        self.metadata = metadata
        self.builtin = builtin