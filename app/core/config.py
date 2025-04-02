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
        "http://localhost",
        "http://localhost:8000",
        "http://localhost:3000",
    ]
    
    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./moss.db"  # 使用异步SQLite驱动
    )

    # LIGHT_RAG
    INPUT_DIR: str = os.getenv(
        "INPUT_DIR",
        "./inputs"
    )
    STORAGE_DIR: str = os.getenv(
        "STORAGE_DIR",
        "./rag_storage"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()