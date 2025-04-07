import json
import logging
from typing import List

import requests
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import StreamingResponse

from app.api.deps import get_db
from app.core.config import settings
from app.core.llm import CompletionsRequest
from app.modules.prompt.biz import prompt as prompt_crud, optimizer_template
from app.modules.prompt.schema.prompt import (
    PromptCreate, PromptInDB, PromptUpdate,
    PromptOptimizeRequest, ChatCompletionResponse
)
from app.modules.prompt.biz.optimizer import optimize_prompt

router = APIRouter()

@router.get("/", response_model=List[PromptInDB])
async def list_prompts(db: AsyncSession = Depends(get_db)):
    """获取提示词列表"""
    prompts = [] # await prompt_crud.get_prompts(db)
    return prompts

@router.get("/{prompt_id}", response_model=PromptInDB)
async def get_prompt(prompt_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个提示词"""
    prompt = await prompt_crud.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="提示词不存在")
    return prompt

@router.post("/", response_model=PromptInDB)
async def create_prompt(
    prompt_in: PromptCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建提示词"""
    prompt = await prompt_crud.create_prompt(db, prompt_in)
    return prompt

@router.put("/{prompt_id}", response_model=PromptInDB)
async def update_prompt(
    prompt_id: int,
    prompt_in: PromptUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新提示词"""
    prompt = await prompt_crud.update_prompt(db, prompt_id, prompt_in)
    if not prompt:
        raise HTTPException(status_code=404, detail="提示词不存在")
    return prompt

@router.post("/optimize")
async def optimize_prompt_text(
    request: PromptOptimizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """优化提示词"""
    logging.info(f"request: {request}")
    try:
        template = await optimizer_template.get_template_by_code(db, request.template_code)
        logging.info(f"template: {template.code}")
        if not template:
            raise HTTPException(status_code=404, detail="优化模板不存在")
        
        request = CompletionsRequest(
            model=request.model,
            messages=[{
                "role": "user",
                "content": request.prompt
            }],
            temperature=0.7,
            stream=request.stream
        )

        messages = request.messages
        if not messages:
            raise HTTPException(status_code=400, detail="消息列表不能为空")

        # 转换消息格式为Ollama格式
        ollama_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # 准备请求数据
        data = {
            "model": request.model or settings.LLM_MODEL_NAME or "deepseek-r1:32b",
            "messages": ollama_messages,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature or 0.5
            }
        }

        if request.stream:
            return StreamingResponse(
                generate_openai_stream(request.messages, request.model),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    # "Content-Type": "text/event-stream",
                    "X-Accel-Buffering": "no",
                }
            )
        else:
            # 非流式请求
            response = requests.post(
                f"{settings.LLM_MODEL_HOST}/v1/chat/completions",
                json=data
            ) if settings.LLM_MODEL == 'ollama' else requests.post(
                f"{settings.LLM_MODEL_HOST}/v1/chat/completions",
                json=data,
            )

            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail=response.text)

            result = response.json()
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": result.get("message", {}).get("content", "")
                    },
                    "finish_reason": "stop",
                    "index": 0
                }]
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def generate_openai_stream(messages: list, model: str = "gpt-3.5-turbo"):
    url = f"{settings.LLM_MODEL_HOST}/api/chat" if settings.LLM_MODEL == 'ollama' else f"{settings.LLM_MODEL_HOST}/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
    }
    data = {
        "model": model,
        "messages": messages,
        "stream": True
    }
    logging.info(f"request: {url}")
    try:
        with requests.post(url, headers=headers, json=data, stream=True) as response:
            logging.info(f"response: {response.text}")
            if response.status_code != 200:
                error = response.json().get("error", {})
                yield json.dumps({
                    "error": {
                        "code": response.status_code,
                        "message": error.get("message", "Unknown error")
                    }
                }) + "\n\n"
                return

            for chunk in response.iter_lines():
                logging.info(f"chunk: {chunk}")
                if chunk:
                    decoded_chunk = chunk.decode('utf-8')

                    if decoded_chunk.startswith("data: [DONE]"):
                        yield "event: done\ndata: {}\n\n"
                        return

                    if not decoded_chunk.startswith("data: "):
                        continue

                    try:
                        json_data = json.loads(decoded_chunk[6:])
                        if "choices" not in json_data:
                            continue

                        for choice in json_data["choices"]:
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                # 封装为 SSE 格式
                                yield f"data: {json.dumps({'content': content})}\n\n"

                    except Exception as e:
                        yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"
                        return

    except Exception as e:
        yield f"event: error\ndata: {json.dumps({'message': str(e)})}\n\n"