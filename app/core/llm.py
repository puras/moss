from typing import List, Optional

from pydantic import BaseModel


# 添加OpenAI请求模型
class ChatMessage(BaseModel):
    role: str
    content: str

class CompletionsRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    stream: Optional[bool] = False
    max_tokens: Optional[int] = None
    mode: Optional[str] = None