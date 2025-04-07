from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.prompt.model.prompt import PromptOptimizerTemplate
from app.modules.prompt.schema.prompt import PromptOptimizerTemplateCreate, PromptOptimizerTemplateUpdate

async def create_template(
    db: AsyncSession, 
    template: PromptOptimizerTemplateCreate
) -> PromptOptimizerTemplate:
    db_template = PromptOptimizerTemplate(**template.model_dump())
    db.add(db_template)
    await db.commit()
    await db.refresh(db_template)
    return db_template

async def get_template(
    db: AsyncSession, 
    template_id: int
) -> Optional[PromptOptimizerTemplate]:
    result = await db.execute(
        select(PromptOptimizerTemplate).filter(PromptOptimizerTemplate.id == template_id)
    )
    return result.scalar_one_or_none()

async def get_templates(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[PromptOptimizerTemplate]:
    result = await db.execute(
        select(PromptOptimizerTemplate)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def update_template(
    db: AsyncSession,
    template_id: int,
    template: PromptOptimizerTemplateUpdate
) -> Optional[PromptOptimizerTemplate]:
    db_template = await get_template(db, template_id)
    if db_template:
        for key, value in template.model_dump(exclude_unset=True).items():
            setattr(db_template, key, value)
        await db.commit()
        await db.refresh(db_template)
    return db_template

async def delete_template(
    db: AsyncSession, 
    template_id: int
) -> bool:
    db_template = await get_template(db, template_id)
    if db_template:
        await db.delete(db_template)
        await db.commit()
        return True
    return False

async def get_template_by_code(
    db: AsyncSession, 
    code: str
) -> Optional[PromptOptimizerTemplate]:
    """根据模板代码查询模板
    
    Args:
        db: 数据库会话
        code: 模板代码
    
    Returns:
        Optional[PromptOptimizerTemplate]: 模板信息
    """
    result = await db.execute(
        select(PromptOptimizerTemplate).filter(PromptOptimizerTemplate.code == code)
    )
    return result.scalar_one_or_none()