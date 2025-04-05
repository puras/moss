import argparse
import asyncio
import logging
import os
import sys
from contextlib import asynccontextmanager

from ascii_colors import ASCIIColors
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from lightrag import LightRAG
from lightrag.api.routers.document_routes import DocumentManager, run_scanning_process
from lightrag.kg.shared_storage import initialize_pipeline_status, get_namespace_data, get_pipeline_status_lock
from lightrag.types import GPTKeywordExtractionFormat
from lightrag.utils import EmbeddingFunc
import pipmaster as pm
from starlette.exceptions import HTTPException

from app.core.config import settings
from app.routes import create_routes
from app.core.logging import setup_logging
from app.util import check_env_file, parse_args, display_splash_screen

# args: argparse.Namespace
def create_app() -> FastAPI:
    doc_manager = DocumentManager(settings.LIGHTRAG_INPUT_DIR)

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

    if settings.LIGHTRAG_LLM_MODEL == 'ollama':
        from lightrag.llm.ollama import ollama_model_complete
    else:
        from lightrag.llm.openai import openai_complete_if_cache

    if settings.LIGHTRAG_EMBED_MODEL == 'ollama':
        from lightrag.llm.ollama import ollama_embed
    else:
        from lightrag.llm.openai import openai_embed

    async def openai_model_complete(
            prompt,
            system_prompt=None,
            history_messages=None,
            keyword_extraction=False,
            **kwargs,
    ) -> str:
        keyword_extraction = kwargs.pop("keyword_extraction", None)
        if keyword_extraction:
            kwargs["response_format"] = GPTKeywordExtractionFormat
        if history_messages is None:
            history_messages = []
        kwargs["temperature"] = settings.LIGHTRAG_LLM_MODEL_TEMPERATURE
        return await openai_complete_if_cache(
            settings.LIGHTRAG_LLM_MODEL_NAME,
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            base_url=settings.LIGHTRAG_LLM_MODEL_HOST,
            api_key=settings.LIGHTRAG_LLM_MODEL_API_KEY,
            **kwargs,
        )

    rag = LightRAG(
        working_dir=settings.LIGHTRAG_STORAGE_DIR,
        llm_model_func=ollama_model_complete
        if settings.LLM_MODEL == 'ollama'
        else openai_model_complete,
        llm_model_name=settings.LIGHTRAG_LLM_MODEL_NAME,
        llm_model_max_async=settings.LIGHTRAG_LLM_MODEL_MAX_ASYNC,
        llm_model_max_token_size=settings.LIGHTRAG_LLM_MODEL_MAX_TOKEN_SIZE,
        llm_model_kwargs={
            "host": settings.LIGHTRAG_LLM_MODEL_HOST,
            "options": {
                "num_ctx": 32768,
                "temperature": settings.LIGHTRAG_LLM_MODEL_TEMPERATURE,
                "prompt_template": settings.LIGHTRAG_LLM_MODEL_PROMPT_TEMPLATE
            },
            "api_key": settings.LIGHTRAG_LLM_MODEL_API_KEY,
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=settings.LIGHTRAG_EMBED_MODEL_DIM,
            max_token_size=settings.LIGHTRAG_EMBED_MODEL_MAX_TOKEN_SIZE,
            func=lambda texts: ollama_embed(
                texts,
                embed_model=settings.LIGHTRAG_EMBED_MODEL_NAME,
                host=settings.LIGHTRAG_EMBED_MODEL_HOST,
                api_key=settings.LIGHTRAG_EMBED_MODEL_API_KEY,
            )
            if settings.LIGHTRAG_EMBED_MODEL=='ollama'
            else openai_embed(
                texts,
                embed_model=settings.LIGHTRAG_EMBED_MODEL_NAME,
                host=settings.LIGHTRAG_EMBED_MODEL_HOST,
                api_key=settings.LIGHTRAG_EMBED_MODEL_API_KEY,
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

def check_and_install_dependencies():
    required_packages = [
        "unicorn",
        "tiktoken",
        "fastapi",
    ]
    for package in required_packages:
        if not pm.is_installed(package):
            print(f"Installing {package}...")
            pm.install(package)
            print(f"{package} installed successfully.")


def main():
    if "GUNICORN_CMD_ARGS" in os.environ:
        print("Running under Gunicorn - worker management handled by Gunicorn.")
        return

    if not check_env_file():
        sys.exit(1)

    setup_logging()

    args = parse_args(is_uvicorn_mode=True)
    display_splash_screen(args)

    # Start Uvicorn in single process mode
    import uvicorn

    uvicorn_config = {
        "host": args.host,
        "port": args.port,
        "log_config": None,  # Disable default config
    }
    if settings.DEBUG:
        print("Starting Uvicorn server in development mode")
        uvicorn_config["app"] = "app.main:create_app"
        uvicorn_config["factory"] = True  # 添加这行
        uvicorn_config["reload"] = settings.DEBUG
    else:
        print("Starting Uvicorn server in production mode")
        app = create_app()
        uvicorn_config["app"] = app

    print(f"Starting Uvicorn server in single-process mode on {args.host}:{args.port}")
    uvicorn.run(**uvicorn_config)

if __name__ == "__main__":
    main()