import json
import logging

from ascii_colors import trace_exception
from fastapi import APIRouter, HTTPException
from lightrag import LightRAG, QueryParam
from lightrag.api.routers.query_routes import QueryResponse, QueryRequest

router = APIRouter(prefix="/chat", tags=["会话"])

def create_chat_routes(rag: LightRAG):
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
                    yield f"{json.dumps({'response': response})}\n"
                else:
                    # If it's an async generator, send chunks one by one
                    try:
                        async for chunk in response:
                            if chunk:  # Only send non-empty content
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

