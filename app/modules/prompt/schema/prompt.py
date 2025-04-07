from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class PromptOptimizerTemplateBase(BaseModel):
    code: str
    name: str
    content: str
    temp_type: str = 'optimizer'
    description: Optional[str] = None
    builtin: bool = True

class PromptOptimizerTemplateCreate(PromptOptimizerTemplateBase):
    pass

class PromptOptimizerTemplateUpdate(PromptOptimizerTemplateBase):
    pass

class PromptOptimizerTemplateInDB(PromptOptimizerTemplateBase):
    id: int
    
    class Config:
        from_attributes = True

class PromptBase(BaseModel):
    name: str
    description: Optional[str] = None
    content: str
    tags: Optional[str] = None
    is_active: Optional[bool] = True

class PromptCreate(PromptBase):
    pass

class PromptUpdate(PromptBase):
    pass

class PromptInDB(PromptBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class PromptOptimizeRequest(BaseModel):
    prompt: str
    model: str = "deepseek-r1:32b"
    template_code: str
    stream: bool = False

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: dict