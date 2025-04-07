from fastapi import APIRouter

from app.modules.prompt.api import prompt_optimizer_template, prompt

router = APIRouter()

router.include_router(prompt_optimizer_template.router, prefix="/optimizer/templates", tags=["prompt_optimizer_template"])
router.include_router(prompt.router, prefix="/prompts", tags=["prompt_optimizer_template"])