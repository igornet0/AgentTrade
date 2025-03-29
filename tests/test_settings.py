from pydantic import DirectoryPath, FilePath
from pydantic_settings import BaseSettings
from pathlib import Path

class SettingsTest(BaseSettings):

    # Пути к данным
    BASE_DIR: DirectoryPath = Path(__file__).resolve().parent
    PATH_DATASETS_TEST: DirectoryPath = BASE_DIR / "test_data"
    PATH_IMG_DATE_TEST: DirectoryPath = PATH_DATASETS_TEST / "test_img_date"

    PATH_DATASET_TEST: FilePath = PATH_DATASETS_TEST / "test_5m.csv"