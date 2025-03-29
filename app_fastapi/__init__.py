from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app_fastapi.configuration.server import Server

import logging
# from apps.settings import Settings

logger = logging.getLogger("app_fastapi")

def create_app(_=None) -> FastAPI:
    app = FastAPI(title="Agent", version="1.0.0")

    # Путь к статическим файлам относительно текущего файла
    static_path = Path(__file__).parent / "static"

    # Создаем папку static если её нет
    static_path.mkdir(exist_ok=True)

    app.mount(
        "/static",
        StaticFiles(directory=static_path, html=True),
        name="static"
    )
    
    # Импортируем роутеры
    # from app_fastapi.parsing.routers import router as parser_router
    # from app_fastapi.processing.routers import process_router
    
    # # Подключаем роутеры к приложению
    # app.include_router(parser_router)
    # app.include_router(process_router)
    
    # return app
    # settings = Settings()
    # app.state.settings = settings
    # app.state.openai = OpenAI()
    
    return Server(app).get_app()