import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.modules.prompt.biz.optimizer_template import (
    create_template,
    get_template,
    get_templates,
    update_template,
    delete_template
)
from app.modules.prompt.schema.prompt import (
    PromptOptimizerTemplateCreate,
    PromptOptimizerTemplateUpdate,
    PromptOptimizerTemplateInDB
)

router = APIRouter()

@router.get("", response_model=List[PromptOptimizerTemplateInDB])
async def list_optimizer_templates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    return await get_templates(db, skip, limit)

@router.post("", response_model=PromptOptimizerTemplateInDB)
async def create_optimizer_template(
    template: PromptOptimizerTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    logging.info(f"Create new optimizer template {template}")
    return await create_template(db, template)


@router.get("/templates/{template_id}", response_model=PromptOptimizerTemplateInDB)
async def get_optimizer_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    template = await get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template

@router.put("/templates/{template_id}", response_model=PromptOptimizerTemplateInDB)
async def update_optimizer_template(
    template_id: int,
    template: PromptOptimizerTemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    db_template = await update_template(db, template_id, template)
    if not db_template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return db_template

@router.delete("/templates/{template_id}")
async def delete_optimizer_template(
    template_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await delete_template(db, template_id)
    if not success:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {"message": "删除成功"}