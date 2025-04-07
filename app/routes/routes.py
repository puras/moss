from fastapi import APIRouter
from lightrag import LightRAG

from app.modules import base, prompt
from app.modules.chat.api import create_chat_routes
from app.modules.edu.ctrl import edu

api_router = APIRouter()

def create_routes(rag: LightRAG):

    # 基础配置
    api_router.include_router(base.router, prefix="/base", tags=["base"])

    # 提示词路由
    api_router.include_router(prompt.router, prefix="/prompt", tags=["提示词"])

    # 会话路由
    api_router.include_router(create_chat_routes(rag))

    api_router.include_router(edu.router, prefix="/edu", tags=["智教"])

    return api_router