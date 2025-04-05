import json
import logging
import requests
from typing import Optional, List, Dict, Any

from ascii_colors import trace_exception
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from lightrag import LightRAG, QueryParam
from lightrag.api.routers.query_routes import QueryRequest, QueryResponse

from app.core.config import settings

router = APIRouter(prefix="/chat", tags=["会话"])

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

def create_chat_routes(rag: LightRAG):
    
    @router.post("/completions")
    async def completions(request: CompletionsRequest):
        try:
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
                async def stream_generator():
                    # 使用requests进行流式请求
                    response = requests.post(
                        f"{settings.LLM_MODEL_HOST}/api/chat",
                        json=data,
                        stream=True
                    ) if settings.LLM_MODEL == 'ollama' else requests.post(
                        f"{settings.LLM_MODEL_HOST}/v1/chat/completions",
                        json=data,
                        stream=True
                    )
                    
                    for line in response.iter_lines():
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
                                
                                # if chunk.get("done", False):
                                #     yield "data: [DONE]\n\n"
                            except json.JSONDecodeError as e:
                                logging.error(f"JSON decode error: {str(e)}")
                                continue

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
            trace_exception(e)
            raise HTTPException(status_code=500, detail=str(e))


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

    @router.post("/rag/query")
    async def rag_query_text(request: QueryRequest):
        try:
            param = request.to_query_params(False)
            response = await rag.aquery(request.query, param=param)

            # If response is a string (e.g. cache hit), return directly
            if isinstance(response, str):
                return QueryResponse(response=response)

            if isinstance(response, dict):
                result = json.dumps(response, indent=2)
                return QueryResponse(response=result)
            else:
                return QueryResponse(response=str(response))
        except Exception as e:
            trace_exception(e)
            raise HTTPException(status_code=500, detail=str(e))

        # # 执行查询
        # results = {
        #     "naive": await rag.query(question, param=QueryParam(mode="naive")),
        #     "local": await rag.query(question, param=QueryParam(mode="local")),
        #     "global": await rag.query(question, param=QueryParam(mode="global")),
        #     "hybrid": await rag.query(question, param=QueryParam(mode="hybrid"))
        # }
        #
        # return results

    @router.post("/rag/query/stream")
    async def rag_query_text_stream(request: QueryRequest):
        """
        This endpoint performs a retrieval-augmented generation (RAG) query and streams the response.

        Args:
            request (QueryRequest): The request object containing the query parameters.
            optional_api_key (Optional[str], optional): An optional API key for authentication. Defaults to None.

        Returns:
            StreamingResponse: A streaming response containing the RAG query results.
        """
        print(request)
        try:
            param = request.to_query_params(True)
            response = await rag.aquery(request.query, param=param)

            from fastapi.responses import StreamingResponse

            async def stream_generator():
                if isinstance(response, str):
                    # If it's a string, send it all at once
                    logging.info(f"response: {json.dumps({'response': response})}")
                    yield f"{json.dumps({'response': response})}\n"
                else:
                    # If it's an async generator, send chunks one by one
                    try:
                        async for chunk in response:
                            if chunk:  # Only send non-empty content
                                logging.info(f"response: {json.dumps({'response': chunk})}")
                                yield f"{json.dumps({'response': chunk})}\n"
                    except Exception as e:
                        logging.error(f"Streaming error: {str(e)}")
                        yield f"{json.dumps({'error': str(e)})}\n"

            return StreamingResponse(
                stream_generator(),
                media_type="application/x-ndjson",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "application/x-ndjson",
                    "X-Accel-Buffering": "no",  # Ensure proper handling of streaming response when proxied by Nginx
                },
            )
        except Exception as e:
            trace_exception(e)
            raise HTTPException(status_code=500, detail=str(e))

    return router

