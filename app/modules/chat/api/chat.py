import json
import logging
import requests

from ascii_colors import trace_exception
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

from lightrag import LightRAG, QueryParam

from app.core.config import settings
from app.core.llm.llm import CompletionsRequest

router = APIRouter(prefix="/chat", tags=["会话"])

async def chat_completions(request: Request, body: CompletionsRequest):  # 修改函数签名
    try:
        messages = body.messages  # 使用 body 替代 request
        if not messages:
            raise HTTPException(status_code=400, detail="消息列表不能为空")

        # 转换消息格式为Ollama格式
        ollama_messages = [{"role": msg.role, "content": msg.content} for msg in messages]

        # 准备请求数据
        data = {
            "model": body.model or settings.LLM_MODEL_NAME or "deepseek-r1:32b",
            "messages": ollama_messages,
            "stream": body.stream,
            "options": {
                "temperature": body.temperature or 0.5
            }
        }

        if body.stream:  # 使用 body 替代 request
            async def stream_generator():
                response = None
                try:
                    # 使用requests进行流式请求
                    response = requests.post(
                        f"{settings.LLM_MODEL_HOST}/api/chat" if settings.LLM_MODEL == 'ollama' else f"{settings.LLM_MODEL_HOST}/v1/chat/completions",
                        json=data,
                        stream=True
                    )
                    
                    for line in response.iter_lines():
                        if await request.is_disconnected():  # 现在可以正确访问 is_disconnected
                            logging.info(f"Request {request.url} disconnected")
                            break
                            
                        if line:
                            try:
                                chunk = json.loads(line)
                                if "error" in chunk:
                                    yield f"data: {json.dumps({'error': chunk['error']})}\n\n"
                                    continue

                                chunk_data = {
                                    "choices": [{
                                        "delta": {"content": chunk.get("message", {}).get("content", "")},
                                        "finish_reason": "stop" if chunk.get("done", False) else None,
                                        "index": 0
                                    }]
                                }
                                yield f"data: {json.dumps(chunk_data)}\n\n"

                            except json.JSONDecodeError as e:
                                logging.error(f"JSON decode error: {str(e)}")
                                continue
                finally:
                    if response:
                        response.close()

            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                    "X-Accel-Buffering": "no",
                }
            )
        else:
            # 非流式请求
            response = requests.post(
                f"{settings.LLM_MODEL_HOST}/v1/chat/completions" if settings.LLM_MODEL == 'ollama' else f"{settings.LLM_MODEL_HOST}/v1/chat/completions",
                json=data
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
        trace_exception(e)
        raise HTTPException(status_code=500, detail=str(e))

def create_chat_routes(rag: LightRAG):
    @router.post("/completions")
    async def completions(request: Request, body: CompletionsRequest):  # 修改路由处理函数
        return await chat_completions(request, body)

    @router.post("/rag/completions")
    async def rag_completions(request: CompletionsRequest):
        try:
            # 将请求转换为RAG查询格式
            messages = request.messages
            if not messages:
                raise HTTPException(status_code=400, detail="消息列表不能为空")

            # 提取最后一条用户消息作为查询
            last_message = messages[-1]
            if last_message.role != "user":
                raise HTTPException(status_code=400, detail="最后一条消息必须是用户消息")

            query = last_message.content
            param = QueryParam(
                mode=request.mode or 'hybird',
                stream=request.stream
            )

            if request.stream:
                # 流式响应
                from fastapi.responses import StreamingResponse

                async def stream_generator():
                    response = await rag.aquery(query, param=param)
                    if isinstance(response, str):
                        chunk_data = {
                            "choices": [{
                                "delta": {"content": response},
                                "finish_reason": "stop",
                                "index": 0
                            }]
                        }
                        yield f"data: {json.dumps(chunk_data)}\n\n"
                    else:
                        try:
                            async for chunk in response:
                                if chunk:
                                    chunk_data = {
                                        "choices": [{
                                            "delta": {"content": chunk},
                                            "finish_reason": None,
                                            "index": 0
                                        }]
                                    }
                                    yield f"data: {json.dumps(chunk_data)}\n\n"
                                else:
                                    chunk_data = {
                                        "choices": [{
                                            "delta": {"content": ""},
                                            "finish_reason": "stop",
                                            "index": 0
                                        }]
                                    }
                                    yield f"data: {json.dumps(chunk_data)}\n\n"
                        except Exception as e:
                            logging.error(f"Streaming error: {str(e)}")
                            yield f"data: {json.dumps({'error': str(e)})}\n\n"

                    # 发送结束标记
                    # yield "data: [DONE]\n\n"

                return StreamingResponse(
                    stream_generator(),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "Content-Type": "text/event-stream",
                        "X-Accel-Buffering": "no",
                    }
                )
            else:
                # 非流式响应
                response = await rag.aquery(query, param=param)
                return {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "content": str(response)
                        },
                        "finish_reason": "stop",
                        "index": 0
                    }]
                }

        except Exception as e:
            trace_exception(e)
            raise HTTPException(status_code=500, detail=str(e))

    return router