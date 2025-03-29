import torch.optim as optim
from App_trade import NewsModel, DatasetTimeseries, NewsDataset
from torch import nn

# Инициализация модели, функции потерь и оптимизатора
model = NewsModel()
criterion = nn.MSELoss()
optimizer = optim.AdamW(model.parameters(), lr=1e-5)

# Пример обучения
# epochs = 3
# for epoch in range(epochs):
#     model.train()
    
#     for batch in train_loader:
#         news_input_ids, news_attention_mask, price_data, targets = batch
        
#         optimizer.zero_grad()
        
#         # Прямой проход через модель  
#         outputs = model(news_input_ids, news_attention_mask, price_data)
#         # Вычисление потерь
#         loss = criterion(outputs, targets)
        
#         # Обратное распространение
#         loss.backward()
#         optimizer.step()

#     print(f'Epoch {epoch+1}, Loss: {loss.item()}')