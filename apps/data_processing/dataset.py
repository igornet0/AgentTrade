from __future__ import annotations

import pandas as pd
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
from pathlib import PosixPath
from urllib.parse import urlparse
from typing import Union
import os
import re

from sklearn.preprocessing import MinMaxScaler
from sktime import utils
from sktime.forecasting.model_selection import temporal_train_test_split

from torch.utils.data import Dataset as _Dataset, DataLoader
from transformers import BertTokenizer
import torch

from core.config import settings_trade
from apps.data_processing.clear_datasets import *
from core.utils.tesseract_img_text import RU_EN_timetravel

import logging

logger = logging.getLogger("process_logger.dataset")

def timer(func):
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        result = func(*args, **kwargs)
        end_time = datetime.now()
        execution_time = end_time - start_time
        logger.info(f"Function {func.__name__} executed in {execution_time}")
        return result
    
    return wrapper

class Dataset(_Dataset):

    def __init__(self, dataset: Union[pd.DataFrame, dict, str], transforms=None, target_column: str=None) -> None:
        
        if isinstance(dataset, str) or isinstance(dataset, PosixPath):
            path_open = self.searh_path_dateset(dataset)
            if isinstance(path_open, list):
                raise FileNotFoundError(f"File {dataset} not found in {os.getcwd()}")
    
            dataset = pd.read_csv(path_open)
            self.set_filename(str(path_open).split("/")[-1])
        else:
            logger.error(f"Invalid dataset type {type(dataset)}")
            self.file_name = "clear_dataset.csv"
        
        self.drop_unnamed(dataset)

        self.dataset = dataset
        self.transforms = transforms

        if target_column:
            self.targets = dataset[target_column]
            self.dataset.drop(target_column, axis=1, inplace=True)
        else:
            self.targets = None

        self.path_save = settings_trade.PROCESSED_DATA_PATH

    def set_filename(self, file_name: str) -> None:
        self.file_name = file_name

    def get_filename(self) -> str:
        return self.file_name

    def get_dataset(self) -> pd.DataFrame:
        return self.dataset
    
    def get_data(self, idx: int):
        return self.dataset.iloc[idx]
    
    @timer
    def clear_dataset(self) -> pd.DataFrame:
        return clear_dataset(self.dataset)

    @classmethod
    def drop_unnamed(cls, dataset):
        try:
            dataset.drop('Unnamed: 0', axis=1, inplace=True)
        except Exception:
            pass

    @classmethod
    def searh_path_dateset(cls, pattern: str, root_dir=os.getcwd()) -> list[str]:
        # Преобразуем шаблон в регулярное выражение
        if os.path.exists(pattern) and os.path.isfile(pattern):
            return pattern

        regex_pattern = '^' + '.*'.join(re.escape(part) for part in pattern.split('*')) + '$'
        regex = re.compile(regex_pattern)
        
        matched_files = []
        
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in filenames:
                if regex.match(filename):
                    full_path = os.path.join(dirpath, filename)
                    matched_files.append(full_path)

        if not matched_files:
            raise FileNotFoundError(f"File {pattern} not found in {root_dir}")
        
        return matched_files
    
    @classmethod
    def concat_dataset(cls, *dataset: pd.DataFrame | Dataset) -> pd.DataFrame:
        return pd.concat([data.get_dataset() if isinstance(data, Dataset) else data for data in dataset], ignore_index=True)
    
    def save_dataset(self) -> None:
        if not os.path.exists(self.path_save):
            os.mkdir(self.path_save)

        self.dataset.to_csv(os.path.join(self.path_save, self.file_name))

        logger.info(f"Dataset saved to {os.path.join(self.path_save, self.file_name)}")

    def __iter__(self):
        for index, data in self.dataset.iterrows():
            yield data

    def __getitem__(self, idx: int):
            
        sample = self.get_data(idx)
        
        if self.transforms:
            sample = self.transforms(sample)

        if self.targets:
            target = self.targets.iloc[idx]
            target = torch.tensor(target, dtype=torch.long)  
            return sample, target

        return sample, self.targets

    def __len__(self):
        return len(self.dataset)


class DatasetTimeseries(Dataset):
    
    def __init__(self, dataset: Union[pd.DataFrame, dict, str] , timetravel: str = "5m") -> None:
        
        super().__init__(dataset)

        if "datetime" not in self.dataset.columns and "date" in self.dataset.columns:
            self.dataset.rename(columns={"date": "datetime"}, inplace=True)

        elif "datetime" not in self.dataset.columns and "date" not in self.dataset.columns:
            raise ValueError("Columns 'datetime' or 'date' not found in dataset")
        elif "open" not in self.dataset.columns:
            raise ValueError("Column 'open' not found in dataset")
        elif "close" not in self.dataset.columns:
            raise ValueError("Column 'close' not found in dataset")
        elif "max" not in self.dataset.columns:
            raise ValueError("Column 'max' not found in dataset")
        elif "min" not in self.dataset.columns:
            raise ValueError("Column 'min' not found in dataset")
        elif "volume" not in self.dataset.columns:
            raise ValueError("Column 'volume' not found in dataset")
        
        self.dataset["datetime"] = self.dataset["datetime"].apply(safe_convert_datetime)
        self.dataset = self.dataset.dropna(subset=["datetime"])

        # "2025-03-18 17:00:00"
        # self.dataset["datetime"] = pd.to_datetime(self.dataset["datetime"], 
        #                                           format="%Y-%m-%d %H:%M:%S",
        #                                           errors='coerce')
        
        # self.dataset = self.dataset.dropna(subset=["datetime"])
            
        self.timetravel = timetravel

    @timer
    def sort(self):
        self.dataset = self.dataset.sort_values(by='datetime', 
                                        ignore_index=True,
                                        ascending=True)
        return self

    @timer
    def clear_dataset(self) -> None:
        # self.dataset = clear_dataset(self.dataset, sort=True, timetravel=self.timetravel)
        dataset = self.dataset.copy()

        for col in dataset.columns:
            if col in ["datetime", "volume"]:
                continue

            dataset[col] = dataset[col].apply(str_to_float) 

        dataset = convert_volume(dataset)
        logger.info("Volume converted to float")

        dataset = dataset.drop_duplicates(subset=['datetime'], ignore_index=True)
        dataset = conncat_missing_rows(dataset, timetravel=self.timetravel)
        logger.info("Missing rows concatenated")

        dataset = dataset.drop_duplicates(subset=['datetime'], ignore_index=True)
        logger.info("Duplicates removed")

        dataset = dataset.sort_values(by='datetime', 
                                        ignore_index=True,
                                        ascending=False)
        logger.info("Dataset sorted")
        self.dataset = dataset
        return self
    
    def set_timetravel(self, timetravel: str):
        if not timetravel in RU_EN_timetravel.keys() or timetravel.isdigit():
            raise ValueError(f"Invalid timetravel: {timetravel}")

        self.timetravel = timetravel
    
    def duplicated(self):
        return self.dataset[self.dataset.duplicated(keep=False)]

    def train_test_split(self, test_size: float = 30) -> None:
        data = self.get_dataset()

        data = data[['datetime', 'close']]  # Предположим, что мы используем только дату и цену закрытия
        data.set_index('datetime', inplace=True)

        # Нормализация данных
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = scaler.fit_transform(data[['close']].values)

        # Генератор данных для обучения
        def create_dataset(data, time_step=1):
            X, y = [], []
            for i in range(len(data) - time_step - 1):
                X.append(data[i:(i + time_step), 0])
                y.append(data[i + time_step, 0])
            return np.array(X), np.array(y)

        time_step = test_size  # Количество временных шагов
        X, y = create_dataset(scaled_data, time_step)
        X = X.reshape(X.shape[0], X.shape[1], 1)  # Преобразуем в 3D массив
        self.train, self.test = temporal_train_test_split(y, X, 
                                                          test_size=test_size)

        utils.plot_series(self.train, self.test, labels=["train", "test"])
        print(self.train.shape, self.test.shape)

        return self.train, self.test

    def plot_series(self, dataset: list | None = None, param: str = "close") -> None:
        plt.figure(figsize=(12, 8))

        if dataset is None:
            y = self.dataset[param]
            utils.plot_series(y)
            plt.title(param)
            plt.tick_params(axis='both', which='major', labelsize=14)

            plt.show()
        else:
            dates = [item['datetime'] for item in dataset]
            closes = [item[param] for item in dataset]

            # Построение графика
            plt.figure(figsize=(10, 5))
            plt.plot(dates, closes, marker='o')
            # plt.title('График цены закрытия')
            plt.xlabel('Время')
            plt.ylabel('Цена')
            plt.xticks(rotation=45)
            plt.grid()
            plt.tight_layout()
            plt.show()

    def get_dataset_Nan(self) -> pd.DataFrame:
        return self.dataset.loc[self.dataset['open'] == "x"]
    
    def dataset_clear(self) -> pd.DataFrame:
        return self.dataset.loc[self.dataset['open'] != "x"]
    
    def get_datetime_last(self) -> datetime:
        return self.dataset['datetime'].iloc[-1]


class NewsDataset(Dataset):

    def __init__(self, dataset, file_path: str, targets=None, tokenizer=BertTokenizer.from_pretrained('bert-base-uncased'), max_len=128):

        """
        Parameters
        ----------
        file_path : str
            Path to file with news texts
        targets : list or None, default=None
            List of targets (labels or values for regression)
        tokenizer : PreTrainedTokenizer, default=BertTokenizer.from_pretrained('bert-base-uncased')
            BERT tokenizer
        max_len : int, default=128
            Maximum length of tokens
        """

        if os.path.exists(file_path):
            file_name = DatasetTimeseries.searh_dateset(dataset)
            file_path = os.path.join(dataset, file_name)
            self.news = pd.read_csv(os.path.join(dataset, file_name),
                                    parse_dates=["datetime"])
            
            if 'Unnamed: 0' in dataset.columns:
                self.news.drop('Unnamed: 0', axis=1, inplace=True)
        else:
            raise ValueError("File not found")

        self.file_path = file_path          
        self.targets = targets                # Целевые значения (метки или значения для регрессии)
        self.tokenizer = tokenizer            # Токенизатор BERT
        self.max_len = max_len                # Максимальная длина токенов
    

    def get_loader(self):
        return DataLoader(self, batch_size=2, shuffle=True)

    
    @classmethod
    def get_domains(cls, news: pd.DataFrame):
        if "url" in news.columns:
            column = "url"
        elif "news_url" in news.columns:
            column = "news_url"
        else:
            return None
        return news[column].apply(lambda x: urlparse(x).netloc).unique().tolist()

    
    def get_news(self):
        return self.news

    def __len__(self):
        return len(self.news)
    
    def __iter__(self):
        for idx in range(len(self)):
            yield self.news.iloc[idx]
    
    def __getitem__(self, idx):
        # Получаем текст новости и его цену по индексу
        news_text = self.news["text"].iloc[idx]
        # prices = self.price_data[idx]
        # target = self.targets[idx]
        
        # Токенизация текста с помощью BERT токенизатора
        encoding = self.tokenizer.encode_plus(
            news_text,
            add_special_tokens=True,
            max_length=self.max_len,
            return_token_type_ids=False,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        # Возвращаем закодированные данные текста, цен и целевую метку
        return {
            'news_input_ids': encoding['input_ids'].flatten(),  # Извлекаем из тензора
            'news_attention_mask': encoding['attention_mask'].flatten(),
            # 'price_data': prices.float(),  # Преобразуем в float для LSTM
            # 'target': torch.tensor(target, dtype=torch.float)  # Целевое значение (например, для регрессии)
        }