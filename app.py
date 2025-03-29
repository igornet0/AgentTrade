from core.utils.configure_logging import setup_logging, format_message
from core.config import settings
import logging

if __name__ == "__main__":
    import uvicorn

    setup_logging()

    logger = logging.getLogger(__name__)
    logger.info("Start server")

    uvicorn.run(
        "app_fastapi:create_app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        factory=True,
        # log_config=None,  # Отключаем стандартное логирование Uvicorn
        # access_log=False  # Мы сами обрабатываем access-логи
    )