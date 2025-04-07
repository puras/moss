from fastapi import APIRouter

from app.modules.base.ctrl import model_provider

router = APIRouter()

router.include_router(model_provider.router, prefix="/providers", tags=["base"])