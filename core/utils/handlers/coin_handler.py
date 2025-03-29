from typing import Generator

from apps import Dataset, DatasetTimeseries
from core.config import settings_trade

class CoinHandler:

    coin_list: list = Dataset(settings_trade.COIN_LIST_PATH).get_dataset()["name"].tolist()

    @classmethod
    def get_coin_list(cls) -> list:
        return cls.coin_list
    
    @classmethod
    def get_path_dataset(cls, coin: str, type_dataset: str = None, timestamp: str = None,
                         root_path: str = settings_trade.PROCESSED_DATA_PATH) -> Generator[list, None, None]:
        
        pattern = f"{coin}*.csv" if timestamp is None else f"{coin}*-{timestamp}.csv"

        pattern = f"{type_dataset}*_{pattern}" if type_dataset is not None else "*" + pattern

        yield DatasetTimeseries.searh_path_dateset(pattern, root_dir=root_path)

