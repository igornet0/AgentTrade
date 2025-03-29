from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app_fastapi.configuration.dependencies import get_async_session

router = APIRouter(prefix="/api_db", tags=["Api db"])


@router.get("/example")
async def example_endpoint(
    session: AsyncSession = Depends(get_async_session)
):
    # Работа с базой данных
    return {"status": "OK"}