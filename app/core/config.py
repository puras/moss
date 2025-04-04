from typing import List
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "MOSS API"
    PROJECT_DESCRIPTION: str = "MOSS Service"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # API配置
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # 安全配置
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALLOWED_ORIGINS: List[str] = [
        "*",
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
    ]
    
    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./moss.db"  # 使用异步SQLite驱动
    )

    LLM_MODEL: str = os.getenv(
        "LLM_MODEL",
        ""
    )
    LLM_MODEL_NAME: str = os.getenv(
        "LLM_MODEL_NAME",
        ""
    )
    LLM_MODEL_HOST: str = os.getenv(
        "LLM_MODEL_HOST",
        ""
    )
    LLM_MODEL_API_KEY: str = os.getenv(
        "LLM_MODEL_API_KEY",
        ""
    )

    # LIGHT_RAG
    LIGHTRAG_LLM_MODEL: str = os.getenv(
        "LIGHTRAG_LLM_MODEL",
        "ollama"
    )
    LIGHTRAG_LLM_MODEL_NAME: str = os.getenv(
        "LIGHTRAG_LLM_MODEL_NAME",
        ""
    )
    LIGHTRAG_LLM_MODEL_MAX_ASYNC: int = os.getenv(
        "LIGHTRAG_LLM_MODEL_MAX_ASYNC",
        4
    )
    LIGHTRAG_LLM_MODEL_MAX_TOKEN_SIZE: int = os.getenv(
        "LIGHTRAG_LLM_MODEL_MAX_TOKEN_SIZE",
        32768
    )
    LIGHTRAG_LLM_MODEL_HOST: str = os.getenv(
        "LIGHTRAG_LLM_MODEL_HOST",
        ""
    )
    LIGHTRAG_LLM_MODEL_API_KEY: str = os.getenv(
        "LIGHTRAG_LLM_MODEL_API_KEY",
        ""
    )
    LIGHTRAG_LLM_MODEL_TEMPERATURE: float = os.getenv(
        "LIGHTRAG_LLM_MODEL_TEMPERATURE",
        0.7
    )
    LIGHTRAG_LLM_MODEL_PROMPT_TEMPLATE: str = os.getenv(
        "LIGHTRAG_LLM_MODEL_PROMPT_TEMPLATE",
        ""
    )
    LIGHTRAG_EMBED_MODEL: str = os.getenv(
        "LIGHTRAG_EMBED_MODEL",
        "ollama"
    )
    LIGHTRAG_EMBED_MODEL_NAME: str = os.getenv(
        "LIGHTRAG_EMBED_MODEL_NAME",
        ""
    )
    LIGHTRAG_EMBED_MODEL_DIM: int = os.getenv(
        "LIGHTRAG_EMBED_MODEL_DIM",
        768
    )
    LIGHTRAG_EMBED_MODEL_HOST: str = os.getenv(
        "LIGHTRAG_EMBED_MODEL_HOST",
        ""
    )
    LIGHTRAG_EMBED_MODEL_API_KEY: str = os.getenv(
        "LIGHTRAG_EMBED_MODEL_API_KEY",
        ""
    )
    LIGHTRAG_EMBED_MODEL_MAX_TOKEN_SIZE: int = os.getenv(
        "LIGHTRAG_EMBED_MODEL_MAX_TOKEN_SIZE",
        8192
    )
    LIGHTRAG_INPUT_DIR: str = os.getenv(
        "LIGHTRAG_INPUT_DIR",
        "./inputs"
    )
    LIGHTRAG_STORAGE_DIR: str = os.getenv(
        "LIGHTRAG_STORAGE_DIR",
        "./rag_storage"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()