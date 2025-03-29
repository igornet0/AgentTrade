import os
from typing import List, Optional

from pydantic import (
    PostgresDsn,
    RedisDsn,
    AmqpDsn,
    Field,
    field_validator,
)

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_core.core_schema import ValidationInfo

class Settings(BaseSettings):
    # Основные настройки приложения
    DEBUG: bool = Field(default=False, description="Режим отладки")
    ENVIRONMENT: str = Field(default="development", description="Окружение (development/production)")
    SECRET_KEY: str = Field(default="secret", description="Секретный ключ приложения")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], description="Разрешенные хосты")
    APP_HOST: str = Field(default="localhost", description="Хост приложения")
    APP_PORT: int = Field(default=8000, description="Порт приложения")

    # Настройки базы данных
    DATABASE_URL: Optional[PostgresDsn] = Field(default=None, description="URL подключения к PostgreSQL")
    DATABASE_ECHO: bool = Field(default=False, description="Логирование SQL запросов")

    # Настройки Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379/0", description="URL подключения к Redis")
    CELERY_BROKER_URL: AmqpDsn = Field(default="amqp://guest:guest@localhost:5672//", description="URL брокера Celery")

    # Настройки бота
    BOT_TOKEN: str = Field(default=..., description="Токен Telegram бота")
    URL_BOT: Optional[str] = Field(default=None, description="URL вебхука для бота")
    ADMINS: List[int] = Field(default=[], description="Список ID администраторов")

    # Настройки биржи
    KUCOIN_API_KEY: str = Field(default=..., description="API ключ KuCoin")
    KUCOIN_API_SECRET: str = Field(default=..., description="API секрет KuCoin")
    KUCOIN_API_PASSPHRASE: str = Field(default=..., description="API парольная фраза KuCoin")

    # Настройки OpenAI/Deepseek
    DEEPSEEK_API_KEY: Optional[str] = Field(default=None, description="API ключ Deepseek")

    # Конфигурация Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @field_validator("ADMINS", mode="before")
    def parse_admins(cls, v: str | List) -> List[int]:
        if not isinstance(v, list):
            return [int(item.strip()) for item in str(v).split(",") if item.strip()]
        return v

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: Optional[str], info: ValidationInfo) -> str:
        if v is None:
            if info.data.get("ENVIRONMENT") == "test":
                return "sqlite:///:memory:"
            raise ValueError("DATABASE_URL must be set in non-test environments")
        return v

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "test"

# Автоматическое создание .env файла, если его нет
if not os.path.exists(".env"):
    with open(".env", "w") as f:
        for field_name, field in Settings.model_fields.items():
            if field.default is not ...:
                f.write(f"{field_name.upper()}={field.default}\n")