import torch
import torch.nn as nn
from transformers import BertModel, BertTokenizer

class CryptoImpactModel(nn.Module):
    def __init__(self, num_coins, coin_names, hidden_dim=256):
        super().__init__()
        self.bert = BertModel.from_pretrained('bert-base-uncased')
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        
        # Coin embeddings layer
        self.coin_embed = nn.Embedding(num_coins, self.bert.config.hidden_size)
        
        # Attention mechanism
        self.attention = nn.MultiheadAttention(
            embed_dim=self.bert.config.hidden_size,
            num_heads=4,
            batch_first=True
        )
        
        # Prediction heads
        self.presence_head = nn.Sequential(
            nn.Linear(self.bert.config.hidden_size * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
        
        self.impact_head = nn.Sequential(
            nn.Linear(self.bert.config.hidden_size * 2, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
            nn.Tanh()
        )
        
        self.coin_names = coin_names
        self.coin2id = {name: idx for idx, name in enumerate(coin_names)}

    def forward(self, input_text):
        # Text processing
        inputs = self.tokenizer(
            input_text,
            return_tensors='pt',
            padding=True,
            truncation=True,
            max_length=512
        ).to(self.bert.device)
        
        text_emb = self.bert(**inputs).last_hidden_state
        
        # Coin embeddings
        coin_ids = torch.tensor([self.coin2id[name] for name in self.coin_names], 
                              device=self.bert.device)
        coin_emb = self.coin_embed(coin_ids)
        
        # Cross-attention between text and coins
        attn_output, _ = self.attention(
            query=coin_emb.unsqueeze(0).repeat(text_emb.size(0), 1, 1),
            key=text_emb,
            value=text_emb
        )
        
        # Concatenate features
        combined = torch.cat([
            coin_emb.unsqueeze(0).repeat(text_emb.size(0), 1, 1),
            attn_output
        ], dim=-1)
        
        # Predictions
        presence = torch.sigmoid(self.presence_head(combined)).squeeze(-1)
        impact = self.impact_head(combined).squeeze(-1) * 100  # Scale to [-100, 100]
        
        return presence, impact

    def predict(self, text, threshold=0.4):
        self.eval()
        with torch.no_grad():
            presence, impact = self.forward(text)
        
        results = []
        for i, coin in enumerate(self.coin_names):
            prob = presence[0][i].item()
            if prob > threshold:
                effect = impact[0][i].item()
                results.append({
                    'coin': coin,
                    'impact': effect,
                    'confidence': prob
                })
        
        return sorted(results, key=lambda x: abs(x['impact']), reverse=True)