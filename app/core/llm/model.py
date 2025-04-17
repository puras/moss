from enum import Enum
from typing import Type


class ModelTypeConst(Enum):
    LLM = {'code': 'LLM', 'message': 'LLM'}
    EMBEDDING = {'code': 'EMBEDDING', 'message': 'Embedding Model'}
    STT = {'code': 'STT', 'message': 'Speech2Text'}
    TTS = {'code': 'TTS', 'message': 'TTS'}
    IMAGE = {'code': 'IMAGE', 'message': 'Vision Model'}
    TTI = {'code': 'TTI', 'message': 'Image Generation'}
    RERANKER = {'code': 'RERANKER', 'message': 'Rerank'}

class ModelInfo:
    def __init__(self, name: str, desc: str, model_type: ModelTypeConst, model_info: dict, model_class: Type, **keywords):
        self.name = name
        self.desc = desc
        self.model_type = model_type.name
        self.model_info = model_info
        if keywords is not None:
            for key in keywords.keys():
                self.__setattr__(key, keywords[key])

    def get_name(self):
        return self.name