from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.prompt.model.prompt import Prompt
from app.modules.prompt.schema.prompt import PromptCreate, PromptUpdate

async def get_prompts(db: AsyncSession) -> List[Prompt]:
    result = await db.execute(select(Prompt))
    return result.scalars().all()

async def get_prompt(db: AsyncSession, prompt_id: int) -> Optional[Prompt]:
    result = await db.execute(select(Prompt).filter(Prompt.id == prompt_id))
    return result.scalar_one_or_none()

async def create_prompt(db: AsyncSession, prompt: PromptCreate) -> Prompt:
    db_prompt = Prompt(**prompt.model_dump())
    db.add(db_prompt)
    await db.commit()
    await db.refresh(db_prompt)
    return db_prompt

async def update_prompt(db: AsyncSession, prompt_id: int, prompt: PromptUpdate) -> Optional[Prompt]:
    db_prompt = await get_prompt(db, prompt_id)
    if db_prompt:
        for key, value in prompt.model_dump(exclude_unset=True).items():
            setattr(db_prompt, key, value)
        await db.commit()
        await db.refresh(db_prompt)
    return db_prompt