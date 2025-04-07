import logging
import time
import uuid
from typing import AsyncGenerator, Union

from app.core.llm import CompletionsRequest, ChatMessage
from app.modules.chat.api import chat_completions
from app.modules.prompt.model.prompt import PromptOptimizerTemplate

async def optimize_prompt(
    prompt: str,
    model: str,
    template: PromptOptimizerTemplate,
    stream: bool = False
) -> Union[dict, AsyncGenerator]:
    """优化提示词"""
    messages = [
        {
            "role": "system",
            "content": template.content
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    request = CompletionsRequest(
        model=model,
        messages=[ChatMessage(role=msg["role"], content=msg["content"]) for msg in messages],
        temperature=0.5,
        stream=stream
    )
    
    return await chat_completions(request)