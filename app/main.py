import asyncio
import logging
import os
from contextlib import asynccontextmanager

from ascii_colors import ASCIIColors
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from lightrag import LightRAG
from lightrag.api.routers.document_routes import DocumentManager, run_scanning_process
from lightrag.kg.shared_storage import initialize_pipeline_status, get_namespace_data, get_pipeline_status_lock
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc
from starlette.exceptions import HTTPException

from app.core.config import settings
from app.routes import create_routes
from app.core.logging import setup_logging

def create_app():

    doc_manager = DocumentManager(settings.INPUT_DIR)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.background_tasks = set()
        # 在应用启动时初始化 LightRAG
        try:
            await rag.initialize_storages()

            await initialize_pipeline_status()
            pipeline_status = await get_namespace_data("pipeline_status")

            should_start_autoscan = False

            if should_start_autoscan:
                task = asyncio.create_task(run_scanning_process(rag, doc_manager))
                app.state.background_tasks.add(task)
                task.add_done_callback(app.state.background_tasks.discard)
                logging.info(f"Process {os.getpid()} auto scan task started at startup.")

            ASCIIColors.green("\nServer is ready to accept connections! 🚀\n")

            yield
        finally:
            await rag.finalize_storages()

    # Initialize FastAPI
    app_kwargs = {
        "title": settings.PROJECT_NAME,
        "description": settings.PROJECT_DESCRIPTION,
        "version": settings.VERSION,
        "openapi_url": f"{settings.API_V1_STR}/openapi.json",  # Explicitly set OpenAPI schema URL
        "docs_url": f"{settings.API_V1_STR}/docs",  # Explicitly set docs URL
        "redoc_url": f"{settings.API_V1_STR}/redoc",  # Explicitly set redoc URL
        "openapi_tags": [{"name": "api"}],
        "lifespan": lifespan,
    }

    app = FastAPI(**app_kwargs)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    rag = LightRAG(
        working_dir=settings.STORAGE_DIR,
        llm_model_func=ollama_model_complete,
        llm_model_name="deepseek-r1:32b",
        llm_model_max_async=4,
        llm_model_max_token_size=32768,
        llm_model_kwargs={
            "host": "http://192.168.0.100:11434",
            "options": {
                "num_ctx": 32768,
                "temperature": 0.7,
                "prompt_template": settings.LLM_PROMPT_TEMPLATE
            },
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embed(
                texts, embed_model="nomic-embed-text", host="http://192.168.0.100:11434"
            ),
        ),
    )

    # 注册路由
    app.include_router(create_routes(rag), prefix=settings.API_V1_STR)

    # 全局异常处理
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "code": exc.status_code,
                "message": str(exc.detail),
                "data": None
            }
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "code": 422,
                "message": "数据验证错误",
                "data": str(exc.errors())
            }
        )

    # 健康检查
    @app.get("/health")
    async def health_check():
        return {
            "code": 200,
            "message": "success",
            "data": {
                "status": "healthy",
                "version": settings.VERSION
            }
        }

    return app


def main():
    setup_logging()
    # Start Uvicorn in single process mode
    import uvicorn
    uvicorn_config = {
        "host": settings.HOST,
        "port": settings.PORT,
        "log_config": None,  # Disable default config
    }
    if settings.DEBUG:
        uvicorn_config["app"] = "app.main:create_app"
        uvicorn_config["reload"] = settings.DEBUG
    else:
        app = create_app()
        uvicorn_config["app"] = app
        uvicorn_config["workers"] = settings.WORKERS

    print(f"Starting Uvicorn server in single-process mode on {settings.HOST}:{settings.PORT}")
    print(uvicorn_config)
    uvicorn.run(**uvicorn_config)

if __name__ == "__main__":
    main()