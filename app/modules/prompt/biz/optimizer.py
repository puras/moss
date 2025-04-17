from typing import AsyncGenerator, Union
from fastapi import Request

from app.core.llm.llm import CompletionsRequest, ChatMessage
from app.modules.chat.api import chat_completions
from app.modules.prompt.model.prompt import PromptOptimizerTemplate

async def optimize_prompt(
        request: Request,
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
    
    request_body = CompletionsRequest(
        model=model,
        messages=[ChatMessage(role=msg["role"], content=msg["content"]) for msg in messages],
        temperature=0.5,
        stream=stream
    )
    
    return await chat_completions(request, request_body)