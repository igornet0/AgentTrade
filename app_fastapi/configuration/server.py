import asyncio 
from fastapi import FastAPI
from app_fastapi.configuration.routers import Routers
from app_fastapi.configuration.lifespan import app_lifespan
from app_fastapi.configuration.dependencies import get_async_session
from core import settings

class Server:

    __app: FastAPI

    def __init__(self, app: FastAPI):
        self.__app = app
        self.__register_routers(app)
        self.__register_dependencies(app)


    def get_app(self) -> FastAPI:
        return self.__app
    
    @staticmethod
    def __register_dependencies(app):
        """Регистрация зависимостей приложения"""
        # Если нужно добавить глобальные зависимости
        app.dependency_overrides.update({
            # Базовые зависимости
            get_async_session: get_async_session
        })

    def __register_routers(self):
        Routers(Routers._discover_routers()).register(self.__app)

    def get_app(self) -> FastAPI:
        return self.__app

    @staticmethod
    def __register_routers(app):

        Routers(Routers._discover_routers()).register(app)

