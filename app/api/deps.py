from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    获取数据库会话依赖
    """
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()