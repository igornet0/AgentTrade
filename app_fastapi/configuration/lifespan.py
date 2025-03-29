from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from core.database.engine import engine, create_db

logger = logging.getLogger(__name__)

@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """Менеджер жизненного цикла приложения"""
    try:
        logger.info("Initializing database...")
        await create_db()
        logger.info("Application startup complete")
        yield
    finally:
        logger.info("Shutting down application...")
        await engine.dispose()
        logger.info("Application shutdown complete")