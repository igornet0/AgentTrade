import numpy as np
import pandas as pd
import torch
from torch import nn

import matplotlib.pyplot as plt

from sktime.forecasting.ets import AutoETS

from sklearn.model_selection import train_test_split


class ModelTrade(nn.Module):

    def __init__(self, input_shape: np.array, prediction_steps: int = 5, flag_lstm: bool = False, flag_save: bool = True, name_model: str = None) -> None:

        self.flag_save = flag_save

        # Параметры
        self.time_steps = 30  # количество рядов
        self.features = 10    # количество значений в каждом ряду
        self.prediction_steps = prediction_steps  # количество предсказаний
        self.output_size = 3  # [buy, sell, hold]

        self.model = self.create_model(input_shape, flag_lstm)

        self.name_model = name_model 
        self.epoch = 0

    def get_model(self):
        return self.model

    def train(self, dataset: pd.DataFrame, test_size: float = 0.2,
                                 epochs: int = 1000, batch_size: int = 32,
                                 optimizer: str = 'adam', loss: str = 'mse', metrics: list = ["accuracy"],
                                 flag_plot: bool = False) -> None:
        
        # Разделение на обучающую и тестовую выборки
        X_train, X_test, y_train, y_test = train_test_split(dataset, test_size=test_size, random_state=42)

        # Компиляция модели
        self.model.compile(optimizer=optimizer, loss=loss)

        # Обучение модели
        history = self.model.fit(X_train, y_train, 
                                 epochs=epochs, 
                                 batch_size=batch_size, validation_split=0.1,
                                 metrics=metrics)
        
        if self.flag_save: 
            self.save()

        if flag_plot:
            self.plot_training_history(history)

        # Оценка модели
        self.test()

    def create_model(self, input_shape, flag_lstm: bool = False):
        if flag_lstm:
            self.model = self.create_lstm_model(input_shape)
            self.name_model = "lstm_model"
        else:
            self.model = self.create_simple_model(input_shape)
            self.name_model = "model_simple"

        return self.model
    
    def predict(self, X: np.array) -> np.array:
        # Прогнозирование
        predictions = self.model.predict(X)

        return predictions
    
    def test(self, dataset_test: pd.DataFrame):
        # Оценка модели
        loss = self.model.evaluate(dataset_test)
        print(f'Test Loss: {loss}')

    def save(self,):
        checkpoint = {
            'epoch': self.epoch,  # Текущая эпоха (пригодится, если захотите продолжить обучение с места остановки)
            'model_state_dict': self.state_dict(),  # Сохранение параметров модели
            'optimizer_state_dict': self.optimizer.state_dict(),  # Сохранение состояния оптимизатора
            'loss': self.buffer_loss,
            'reward': self.buffer_reward
        }
        torch.save(checkpoint, f"{self.epoch}_{self.name_model}")  # Сохранение в файл
        # print(f"Модель успешно сохранена на {self.name_model}")

    @staticmethod
    def plot_training_history(history):
        # Получаем данные из истории
        metrics = history.history.keys()
        
        # Создаем графики для каждой метрики
        plt.figure(figsize=(12, 8))
        
        for metric in metrics:
            plt.plot(history.history[metric], label=metric)
        
        # Настройки графика
        plt.title('Training History')
        plt.xlabel('Epochs')
        plt.ylabel('Value')
        plt.legend()
        plt.grid()
        plt.show()
    
    @staticmethod
    def create_news_model(input_shape):
        pass

class ModelTest:

    def __init__(self) -> None:
        
        self.forecaster = AutoETS(auto=True, 
                                  n_jobs=-1, 
                                  trend="add",
                                  information_criterion="bic")
        
    def fit(self, dataset: pd.DataFrame):

        self.forecaster.fit(dataset)

        y_pred = self.forecaster.predict(n_periods=dataset.shape[0])
        
        return y_pred

