import logging
import time
import uuid
from typing import AsyncGenerator, Union

from app.core.llm import CompletionsRequest
from app.modules.prompt.model.prompt import PromptOptimizerTemplate

async def optimize_prompt(
    prompt: str,
    model: str,
    template: PromptOptimizerTemplate,
    stream: bool = False
) -> Union[dict, AsyncGenerator]:
    """优化提示词"""
    optimization_prompt = template.content.format(
        prompt=prompt
    )
    
    request = CompletionsRequest(
        model=model,
        messages=[{
            "role": "user",
            "content": optimization_prompt
        }],
        temperature=0.7,
        stream=stream
    )
    
    # return await chat_completions(request)