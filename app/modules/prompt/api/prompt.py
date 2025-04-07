import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.modules.prompt.biz import prompt as prompt_crud, optimizer_template
from app.modules.prompt.biz.optimizer import optimize_prompt
from app.modules.prompt.schema.prompt import (
    PromptCreate, PromptInDB, PromptUpdate,
    PromptOptimizeRequest
)

router = APIRouter()

@router.get("/", response_model=List[PromptInDB])
async def list_prompts(db: AsyncSession = Depends(get_db)):
    """获取提示词列表"""
    prompts = [] # await prompt_crud.get_prompts(db)
    return prompts

@router.get("/{prompt_id}", response_model=PromptInDB)
async def get_prompt(prompt_id: int, db: AsyncSession = Depends(get_db)):
    """获取单个提示词"""
    prompt = await prompt_crud.get_prompt(db, prompt_id)
    if not prompt:
        raise HTTPException(status_code=404, detail="提示词不存在")
    return prompt

@router.post("/", response_model=PromptInDB)
async def create_prompt(
    prompt_in: PromptCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建提示词"""
    prompt = await prompt_crud.create_prompt(db, prompt_in)
    return prompt

@router.put("/{prompt_id}", response_model=PromptInDB)
async def update_prompt(
    prompt_id: int,
    prompt_in: PromptUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新提示词"""
    prompt = await prompt_crud.update_prompt(db, prompt_id, prompt_in)
    if not prompt:
        raise HTTPException(status_code=404, detail="提示词不存在")
    return prompt

@router.post("/optimize")
async def optimize_prompt_text(
    request: PromptOptimizeRequest,
    db: AsyncSession = Depends(get_db)
):
    """优化提示词"""
    logging.info(f"request: {request}")
    template = await optimizer_template.get_template_by_code(db, request.template_code)
    logging.info(f"template: {template.code}")
    if not template:
        raise HTTPException(status_code=404, detail="优化模板不存在")

    return await optimize_prompt(request.prompt, request.model, template, request.stream)