import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt

from sktime.forecasting.ets import AutoETS

from sklearn.model_selection import train_test_split

from .NN_GeneratorDataset import GeneratorDataset

    

class ModelTrade:

    def __init__(self, input_shape: np.array, prediction_steps: int = 5, flag_lstm: bool = False, flag_save: bool = True) -> None:

        self.flag_save = flag_save

        # Параметры
        self.time_steps = 30  # количество рядов
        self.features = 10    # количество значений в каждом ряду
        self.prediction_steps = prediction_steps  # количество предсказаний
        self.output_size = 3  # [buy, sell, hold]

        self.model = self.create_model(input_shape, flag_lstm)

    def get_model(self) -> tf.keras.Model:
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

    def create_model(self, input_shape, flag_lstm: bool = False) -> tf.keras.Model:
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

    def save(self, name_model: str = None):
        if name_model:
            self.name_model = name_model

        self.model.save(f"{self.name_model}.keras")

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

    def create_prediction_model(self, x):
        # Входной слой для второй модели
        second_model_input = tf.keras.layers.RepeatVector(self.prediction_steps)(x)

        # Слои второй модели
        y = tf.keras.layers.LSTM(32)(second_model_input)
        y = tf.keras.layers.Dense(1)(y)  # Выходное значение для закрытия следующего ряда

        # Генерация предсказаний
        predictions = []
        for _ in range(self.prediction_steps):
            if len(predictions) > 0:
                # Если это не первое предсказание, добавляем предсказанное значение в входные данные
                new_input = tf.keras.layers.Concatenate()([second_model_input, tf.keras.layers.Dense(1)(predictions[-1])])
            else:
                new_input = second_model_input
            
            y = tf.keras.layers.LSTM(32)(new_input)
            pred = tf.keras.layers.Dense(1)(y)
            predictions.append(pred)
        
        return predictions

    def create_model(self):

        input_layer = tf.keras.layers.Input(shape=(self.time_steps, self.features))

        # Слои первой модели
        x = tf.keras.layers.LSTM(64, return_sequences=True)(input_layer)
        x = tf.keras.layers.LSTM(32)(x)

        # Слои второй модели
        predictions_price = self.create_prediction_model(x)
        predictions_news = self.create_news_model(x)

        # Объединяем все предсказания в одном тензоре
        predictions_output_price = tf.keras.layers.Concatenate(axis=1)(predictions_price)
        predictions_output_news = tf.keras.layers.Concatenate(axis=1)(predictions_news)

        # Обработка выходных данных первой модели
        combined_output = tf.keras.layers.Concatenate()([x, predictions_output_price, predictions_output_news, input_layer[-1]])

        # Финальные слои для классификации [buy, sell, hold]
        final_output = tf.keras.layers.Dense(self.output_size, activation='softmax')(combined_output)

        # Создание модели
        model = tf.keras.Model(inputs=input_layer, outputs=final_output)

        return model
    
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

