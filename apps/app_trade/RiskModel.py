import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

class RiskAssessmentModel(nn.Module):
    def __init__(self,
                 lstm_input_size=1,       # число признаков для исторических данных (например, цена)
                 lstm_hidden_size=64,      # размер скрытого состояния LSTM
                 lstm_layers=2,            # число слоёв LSTM
                 order_feature_size=3,     # число признаков заявки (например, тип, цена, объём)
                 fc_order_size=32,         # размер скрытого представления для данных заявки
                 combined_fc_size=32       # размер скрытого слоя после объединения
                 ):
        super(RiskAssessmentModel, self).__init__()
        # LSTM для обработки исторических цен (вход имеет форму [batch, seq_len, lstm_input_size])
        self.lstm = nn.LSTM(input_size=lstm_input_size, 
                            hidden_size=lstm_hidden_size,
                            num_layers=lstm_layers, 
                            batch_first=True)
        # Полносвязная сеть для обработки характеристик заявки
        self.fc_order = nn.Sequential(
            nn.Linear(order_feature_size, fc_order_size),
            nn.ReLU()
        )
        # Слои для объединения признаков LSTM и данных заявки
        self.fc_combined = nn.Sequential(
            nn.Linear(lstm_hidden_size + fc_order_size, combined_fc_size),
            nn.ReLU(),
            nn.Linear(combined_fc_size, 1),
            nn.Sigmoid()  # выход – вероятность риска от 0 до 1
        )
    
    def forward(self, price_history, order_features):
        """
        :param price_history: Tensor формы (batch_size, seq_len, lstm_input_size)
        :param order_features: Tensor формы (batch_size, order_feature_size)
        :return: риск заявки – Tensor формы (batch_size, 1)
        """
        # Проходим последовательность через LSTM.
        # Получаем выход, а также последнее скрытое состояние для каждого слоя.
        lstm_out, (h_n, c_n) = self.lstm(price_history)
        # Используем скрытое состояние последнего слоя как представление временной динамики:
        lstm_feat = h_n[-1]  # форма: (batch_size, lstm_hidden_size)
        
        # Обработка характеристик заявки
        order_feat = self.fc_order(order_features)  # форма: (batch_size, fc_order_size)
        
        # Объединение обоих представлений
        combined = torch.cat([lstm_feat, order_feat], dim=1)
        
        # Итоговая оценка риска
        risk = self.fc_combined(combined)
        return risk

# Пример создания модели:
model = RiskAssessmentModel()

def train():

    # Пример гиперпараметров
    num_epochs = 50
    learning_rate = 1e-3
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.BCELoss()  # так как выход – вероятность риска

    # Допустим, у вас есть DataLoader-ы: train_loader и valid_loader
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    for epoch in range(num_epochs):
        model.train()
        train_loss = 0.0
        for batch in train_loader:
            # Предположим, батч содержит:
            # price_history: (batch_size, seq_len, 1)
            # order_features: (batch_size, 3)
            # target_risk: (batch_size, 1) – метка риска (0 или 1)
            price_history = batch['price_history'].to(device)
            order_features = batch['order_features'].to(device)
            target = batch['target_risk'].to(device).float()
            
            optimizer.zero_grad()
            output = model(price_history, order_features)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * price_history.size(0)
        
        train_loss /= len(train_loader.dataset)
        
        # Валидация
        model.eval()
        valid_loss = 0.0
        with torch.no_grad():
            for batch in valid_loader:
                price_history = batch['price_history'].to(device)
                order_features = batch['order_features'].to(device)
                target = batch['target_risk'].to(device).float()
                
                output = model(price_history, order_features)
                loss = criterion(output, target)
                valid_loss += loss.item() * price_history.size(0)
        valid_loss /= len(valid_loader.dataset)
        
        print(f"Epoch {epoch+1}/{num_epochs}  Train Loss: {train_loss:.4f}  Valid Loss: {valid_loss:.4f}")