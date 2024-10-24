import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from urllib.parse import urlparse

from sklearn.preprocessing import MinMaxScaler
from sktime import utils
from sktime.forecasting.model_selection import temporal_train_test_split

from torch.utils.data import Dataset as _Dataset, DataLoader
from transformers import BertTokenizer
import torch

from typing import Union
from os import listdir, mkdir, getcwd, path

from .clear_datasets import *


class Dataset(_Dataset):

    def __init__(self, dataset: Union[pd.DataFrame, str], save: bool = True, path_save: str = "datasets", 
                 file_name: str = "clear_dataset.csv") -> None:
        
        if isinstance(dataset, str):
            file_name = self.searh_dateset(dataset)
            dataset = pd.read_csv(file_name)

            if 'Unnamed: 0' in dataset.columns:
                dataset.drop('Unnamed: 0', axis=1, inplace=True)

        self.dataset = dataset
        self.save = save
        self.path_save = path_save
        self.file_name = file_name
        self.main_dir = getcwd()

    @classmethod
    def searh_dateset(cls, path: str) -> str:
        if path.endswith(".csv"):
            return path
        
        return path.join(path, [f for f in listdir(path) if f.endswith(".csv")][0])
    
    def get_dataset(self) -> pd.DataFrame:
        return self.dataset
    
    def concat_dataset(self, dataset: pd.DataFrame) -> pd.DataFrame:
        if isinstance(dataset, DatasetTimeseries):
            dataset = dataset.dataset_clear()
        else:
            raise ValueError("Dataset must be DatasetTimeseries")

        self.dataset = pd.concat([self.dataset_clear(), dataset], ignore_index=True)

        self.process()

        return self.dataset
    
    def save_dataset(self) -> None:
        if not path.exists(self.path_save):
            mkdir(self.path_save)

        self.dataset.to_csv(path.join(self.path_save, self.file_name))


class DatasetTimeseries(Dataset):
    def __init__(self, dataset: pd.DataFrame, timetravel: str = "5m",
                 save : bool = True, 
                 path_save: str = "datasets_tine", file_name: str = "time_dataset.csv") -> None:
        
        super().__init__(dataset, save, path_save, file_name)

        if "datetime" not in self.dataset.columns and "date" in self.dataset.columns:
            self.dataset.rename(columns={"date": "datetime"}, inplace=True)

        elif "datetime" not in self.dataset.columns and "date" not in self.dataset.columns:
            raise ValueError("Columns 'datetime' and 'date' not found in dataset")
        
        self.dataset["datetime"] = pd.to_datetime(self.dataset["datetime"])
            
        self.timetravel = timetravel

    def process(self) -> None:
        self.dataset = clear_dataset(self.dataset, sort=True, timetravel=self.timetravel)

        if self.save:
            self.save_dataset()

        return self.dataset

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


    def plot_series(self, param: str = "close") -> None:
        plt.figure(figsize=(12, 8))

        y = self.dataset[param]


        utils.plot_series(y)
        plt.title(param)
        plt.tick_params(axis='both', which='major', labelsize=14)

        plt.show()

    
    def get_dataset_Nan(self) -> pd.DataFrame:
        return self.dataset.loc[self.dataset['open'] == "x"]
    
    def dataset_clear(self) -> pd.DataFrame:
        return self.dataset.loc[self.dataset['open'] != "x"]
    
    def get_datetime_last(self) -> datetime:
        return self.dataset['datetime'].iloc[-1]
    
    def concat_dataset(self, dataset: pd.DataFrame) -> pd.DataFrame:
        if isinstance(dataset, DatasetTimeseries):
            dataset = dataset.dataset_clear()
        else:
            raise ValueError("Dataset must be DatasetTimeseries")

        self.dataset = pd.concat([self.dataset_clear(), dataset], ignore_index=True)

        self.process()

        return self.dataset
    
    def get_filename(self) -> str:
        return self.file_name


    def __getitem__(self, date):
        pass


    def __len__(self):
        return len(self.dataset)


class NewsDataset(Dataset):
    def __init__(self, file_path: str, targets=None, tokenizer=BertTokenizer.from_pretrained('bert-base-uncased'), max_len=128):

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

        if path.exists(file_path):
            file_name = DatasetTimeseries.searh_dateset(dataset)
            file_path = path.join(dataset, file_name)
            self.news = pd.read_csv(path.join(dataset, file_name),
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