from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.engine import session_maker

async def get_async_session() -> AsyncSession:
    """Генератор асинхронных сессий для DI"""
    async with session_maker() as session:
        yield session