from core.config import settings, settings_trade
import logging
from logging.handlers import RotatingFileHandler
# from core.utils.error_handler_logging import ErrorHandlerImg

format_message = '%(asctime)s] %(name)-35s:%(lineno)-3d - %(levelname)-7s - %(message)s'

logging.getLogger("selenium").setLevel(logging.WARNING)
logging.getLogger("undetected_chromedriver").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)
# logging.getLogger("uvicorn").setLevel(logging.INFO)
# logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

def setup_logging():
    # Очищаем все существующие обработчики
    for logger in [logging.getLogger(name) for name in logging.root.manager.loggerDict]:
        logger.handlers = []

    level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Корневой логгер (все сообщения)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Форматтер для всех логов
    formatter = logging.Formatter(format_message)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Общий файловый хендлерs
    common_handler = RotatingFileHandler(settings_trade.LOG_PATH / "all.log", maxBytes=1e6, backupCount=3)
    common_handler.setFormatter(formatter)

    # Настройка логгеров Uvicorn
    # uvicorn_handler = RotatingFileHandler(settings_trade.LOG_PATH / "uvicorn.log", maxBytes=1e6, backupCount=3)
    # uvicorn_handler.setFormatter(formatter)

    # uvicorn_access_handler = RotatingFileHandler(settings_trade.LOG_PATH / "uvicorn_access.log", maxBytes=5e6, backupCount=5)
    # access_formatter = logging.Formatter('%(asctime)s] %(name)-35s:%(client_addr)s - "%(request_line)s" %(status_code)s')
    # uvicorn_access_handler.setFormatter(access_formatter)

    # uvicorn_logger = logging.getLogger("uvicorn")
    # uvicorn_logger.handlers = [uvicorn_handler]
    # uvicorn_logger.propagate = False
    
    # uvicorn_access_logger = logging.getLogger("uvicorn.access")
    # uvicorn_access_logger.handlers = [uvicorn_access_handler]
    # uvicorn_access_logger.propagate = False
    
    # uvicorn_error_logger = logging.getLogger("uvicorn.error")
    # uvicorn_error_logger.handlers = [uvicorn_handler]
    # uvicorn_error_logger.propagate = False

    # Настройка для app_fastapi
    app_fastapi_logger = logging.getLogger("app_fastapi")
    app_fastapi_handler = RotatingFileHandler(settings_trade.LOG_PATH / "app_fastapi.log", maxBytes=1e6, backupCount=3)
    app_fastapi_handler.setFormatter(formatter)
    app_fastapi_handler.setLevel(logging.DEBUG)
    app_fastapi_logger.addHandler(app_fastapi_handler)

    # Настройка для parser_logger
    parser_logger = logging.getLogger("parser_logger")
    parser_handler = RotatingFileHandler(settings_trade.LOG_PATH / "parser_logger.log", maxBytes=1e6, backupCount=3)
    parser_handler.setFormatter(formatter)
    parser_handler.setLevel(logging.DEBUG)
    parser_logger.addHandler(parser_handler)

    process_logger = logging.getLogger("process_logger")
    process_handler = RotatingFileHandler(settings_trade.LOG_PATH / "process_logger.log", maxBytes=1e6, backupCount=3)
    process_handler.setFormatter(formatter)
    process_handler.setLevel(logging.DEBUG)
    process_logger.addHandler(process_handler)

    # root_logger.addHandler(app_fastapi_handler)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(common_handler)