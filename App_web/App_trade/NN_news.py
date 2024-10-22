import torch
import torch.nn as nn
from transformers import BertModel
from transformers import BertTokenizer

class NewsModel(nn.Module):
    def __init__(self, bert_model_name='bert-base-uncased', price_input_size=10, hidden_size=128):
        super(NewsModel, self).__init__()
        
        # Модель для обработки текста
        self.bert = BertModel.from_pretrained(bert_model_name)

        # Инициализация токенизатора BERT
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        
        # LSTM для обработки временного ряда
        self.lstm_price = nn.LSTM(input_size=price_input_size, hidden_size=hidden_size, num_layers=2, batch_first=True)
        
        # Полносвязные слои для объединения признаков
        self.fc1 = nn.Linear(hidden_size + self.bert.config.hidden_size, 64)
        self.fc2 = nn.Linear(64, 1)  # Один выход для регрессии (например, изменение цены)
        
    def preprocess_text(self, news_texts, max_len=128):
        encoding = self.tokenizer(news_texts, 
                            padding='max_length',  # Делаем одинаковую длину для всех текстов
                            truncation=True,       # Усечение текста до max_len
                            max_length=max_len, 
                            return_tensors='pt')   # Возвращаем данные в виде PyTorch тензоров
        
        return encoding['input_ids'], encoding['attention_mask']
        
    def forward(self, news_input_ids, news_attention_mask, price_data):
        # Обработка текста через BERT
        bert_output = self.bert(input_ids=news_input_ids, attention_mask=news_attention_mask)
        news_features = bert_output.pooler_output
        
        # Обработка временного ряда цен через LSTM
        lstm_out, _ = self.lstm_price(price_data)
        price_features = lstm_out[:, -1, :]  # Берем последний выход LSTM
        
        # Объединение признаков
        combined_features = torch.cat((news_features, price_features), dim=1)
        
        # Полносвязные слои для регрессии
        x = torch.relu(self.fc1(combined_features))
        output = self.fc2(x)
        
        return output