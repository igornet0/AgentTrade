from typing import Dict
import torch
from core.config import settings
from .model_loader import ModelLoader
from .preprocessor import DataPreprocessor

class ModelService:
    def __init__(self):
        self.models: Dict[str, dict] = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
    async def load_model(self, config_path: str):
        """Загрузка модели из конфига"""
        loader = ModelLoader(device=self.device)
        model, metadata = loader.from_config(config_path)
        self.models[metadata['name']] = {
            'model': model,
            'metadata': metadata,
            'preprocessor': DataPreprocessor(**metadata['preprocessing'])
        }

    async def predict(self, model_name: str, data):
        """Выполнение предсказания"""
        model_data = self.models.get(model_name)
        if not model_data:
            raise ValueError("Model not loaded")
        
        processed_data = model_data['preprocessor'](data)
        with torch.no_grad():
            outputs = model_data['model'](processed_data)
        return outputs.numpy()