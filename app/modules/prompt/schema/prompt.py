from datetime import datetime
from typing import Optional
from pydantic import BaseModel

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