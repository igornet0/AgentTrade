import pandas as pd
import numpy as np

from tensorflow.keras.models import Model

class Test:
    def __init__(self, dataset: pd.DataFrame, model: Model) -> None:
        self.dataset = dataset

        self.model = model

    def process(self) -> None:
        pass




# Класс торгового агента
class TradingAgent:
    def __init__(self, ticker='AAPL', start_date='2020-01-01', end_date='2023-01-01'):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        
        # Инициализируем модели и параметры
        self.sentiment_model = NewsModel()
        self.scaler = StandardScaler()
        self.lstm_model = LSTMModel()
        self.policy_network = PolicyNetwork()
        self.lasso = Lasso(alpha=0.1)
        self.xgb_model = None

        # Загружаем данные и готовим их
        self.data = self.download_data()
        self.sentiment_scores = self.sentiment_model.get_sentiment_scores(self.data['news'])
        self.data['Sentiment'] = self.sentiment_scores
        self.prepare_features()

    def download_data(self):
        # Скачиваем исторические данные
        data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
        data['Return'] = data['Close'].pct_change()
        data['MA_10'] = data['Close'].rolling(window=10).mean()
        data['MA_50'] = data['Close'].rolling(window=50).mean()
        data['Volume_Change'] = data['Volume'].pct_change()
        data['news'] = ["Example news"] * len(data)  # Здесь замените на реальные новости по дням
        data.dropna(inplace=True)
        return data

    def prepare_features(self):
        # Подготовка данных для моделей
        features = self.data[['MA_10', 'MA_50', 'Volume_Change', 'Sentiment']].values
        target = self.data['Return'].values

        # Масштабируем данные для модели
        self.X = self.scaler.fit_transform(features)
        self.y = target

    def train_lstm(self, sequence_length=50, epochs=10):
        # Обучаем модель LSTM на данных
        dataset = TimeSeriesDataset(self.X, self.y, sequence_length)
        loader = DataLoader(dataset, batch_size=32, shuffle=True)
        optimizer = torch.optim.Adam(self.lstm_model.parameters(), lr=0.001)
        criterion = nn.MSELoss()

        for epoch in range(epochs):
            for inputs, targets in loader:
                inputs = inputs.unsqueeze(-1)  # Добавляем размерность
                targets = targets.unsqueeze(-1)
                outputs = self.lstm_model(inputs)
                loss = criterion(outputs, targets)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            print(f'Epoch {epoch+1}, Loss: {loss.item()}')

    def train_lasso(self):
        # Обучение Lasso-регрессии для оценки влияния настроений на доходность
        self.lasso.fit(self.X, self.y)
        print("Коэффициенты влияния настроений на цену:", self.lasso.coef_)

    def train_xgb(self):
        # Обучение модели XGBoost для прогнозирования
        dtrain = xgb.DMatrix(self.X, label=self.y)
        params = {'objective': 'reg:squarederror', 'max_depth': 4, 'eta': 0.1}
        self.xgb_model = xgb.train(params, dtrain, num_boost_round=100)

    def predict_with_xgb(self, features):
        dtest = xgb.DMatrix(features)
        return self.xgb_model.predict(dtest)
    
    def trade(self, state):
        # Оптимизация объема позиций на основе нейронной сети
        action = self.policy_network(torch.tensor(state, dtype=torch.float32))
        return action.item()

    def evaluate_strategy(self):
        # Оценка стратегии на исторических данных
        balance = 1000  # Начальный баланс
        for i in range(len(self.data) - 50):
            state = self.data.iloc[i:i+50][['MA_10', 'MA_50', 'Volume_Change', 'Sentiment']].values
            state_scaled = self.scaler.transform(state)
            predicted_return = self.predict_with_xgb(state_scaled[-1:])
            position_size = self.trade(state_scaled[-1:])
            balance += position_size * predicted_return  # Простая модель обновления баланса
        print(f"Итоговый баланс: {balance}")

# Дополнительные классы
class TimeSeriesDataset(Dataset):
    def __init__(self, X, y, sequence_length=50):
        self.X = X
        self.y = y
        self.sequence_length = sequence_length

    def __len__(self):
        return len(self.X) - self.sequence_length

    def __getitem__(self, index):
        x = self.X[index:index+self.sequence_length]
        y = self.y[index+self.sequence_length]
        return torch.tensor(x, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)

class LSTMModel(nn.Module):
    def __init__(self, input_size=1, hidden_size=50, num_layers=2):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        h0 = torch.zeros(2, x.size(0), 50).to(x.device)
        c0 = torch.zeros(2, x.size(0), 50).to(x.device)
        out, _ = self.lstm(x, (h0, c0))
        out = self.fc(out[:, -1, :])
        return out

class PolicyNetwork(nn.Module):
    def __init__(self, input_size=4, hidden_size=128, output_size=1):
        super(PolicyNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.tanh(self.fc2(x))  # Выход между -1 и 1 для размера позиции
        return x