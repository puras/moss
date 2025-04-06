from fastapi import APIRouter
from lightrag import LightRAG

from app.modules.chat.ctrl import create_chat_routes
from app.modules.edu.ctrl import edu
from app.modules.prompt.ctrl import prompts

api_router = APIRouter()

def create_routes(rag: LightRAG):

    # 提示词路由
    api_router.include_router(prompts.router, prefix="/prompts", tags=["提示词"])
    api_router.include_router(create_chat_routes(rag))

    api_router.include_router(edu.router, prefix="/edu", tags=["智教"])
    return api_router