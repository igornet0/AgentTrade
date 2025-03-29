from pathlib import Path
from typing import Optional, Literal

from pydantic import (
    Field,
    DirectoryPath,
    FilePath
)
from pydantic_settings import BaseSettings

class SettingsTrade(BaseSettings):

    # Пути к данным
    BASE_DIR: DirectoryPath = Path(__file__).resolve().parent.parent.parent
    DATA_DIR: DirectoryPath = BASE_DIR / "data"
    RAW_DATA_PATH: DirectoryPath = DATA_DIR / "raw"
    CACHED_DATA_PATH: DirectoryPath = DATA_DIR / "cached"
    PROCESSED_DATA_PATH: DirectoryPath = DATA_DIR / "processed"
    BACKUP_DATA_PATH: DirectoryPath = DATA_DIR / "backup"
    TRACH_PATH: DirectoryPath = DATA_DIR / "trach"
    LOG_PATH: DirectoryPath = DATA_DIR / "log"
    
    COIN_LIST_PATH: FilePath = DATA_DIR / "coin_list.csv"

    TYPE_DATASET_FOR_COIN: Optional[Literal["clear", "train", "test"]] = Field(default="clear", description="Тип датасета (clear, train, test) для сохранения в БД")
    TIMETRAVEL: Optional[str] = Field(default="5m", description="Временная метка данных")

    # Модели ML
    MODELS_DIR: DirectoryPath = BASE_DIR / "models"
    MODELS_CONFIGS_PATH: DirectoryPath = MODELS_DIR / "model_configs"
    # ACTIVE_MODEL: FilePath = TRAINED_MODELS_PATH / "current_model.pkl"

    URL_KUCOIN: str = "https://www.kucoin.com/ru/trade/{coin}-USDT"
    
URL_SETTINGS = {
    # "https://ambcrypto.com/category/new-news/":{
    #     "next_page": "load more articles",
    #     "filter_text": lambda x: len(x) > 26,
    #     "news": {
    #         "SHOW": True,
    #         "SCROLL": -1000,
    #         "ZOOM": 0.6,
    #         "text_start": "title",
    #         "text_end": ["Disclaimer:"],
    #         "tag_end": ["a//take a survey:"],
    #         "text_continue": ["2min", "source:"],
    #         "img_continue": ["alt@avatar"],
    #         "date_format": "posted: %B %d, %Y",
    #         "filter_tags": ["h1", "h2", "p", "em", "span", "img"]
    #         }
    #     },
    # "https://cryptoslate.com/crypto/":{
    #     "CAPTHA": True,
    #     "next_page": "next page",
    #     "filter_text": lambda x: len(x) > 20,
    #     "clear": True,
    #     "news": {
    #         "SHOW": True,
    #         "SCROLL": -1000,
    #         "ZOOM": 0.6,
    #         "text_start": "title",
    #         "tag_end": ["div//Posted In:"],
    #         "text_continue": ["2min", "source:"],
    #         "img_continue": ["data-del@avatar"],
    #         "date_format": "Updated: %b. %d, %Y at %I:%M %p %Z",
    #         "filter_tags": ["h1", "h2", "p", "em", "span", "img"]
    #         }
    # },
    
    "telegram":{
        "CAPTHA": False,
        "chanels": {
            "🔥Full-Time Trading": {
                "filter_text": ["#Крипта"]
            },
        }
    }
}