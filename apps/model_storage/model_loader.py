import yaml
import torch
from pathlib import Path

class ModelLoader:
    def __init__(self, device='cpu'):
        self.device = device

    def from_config(self, config_path: str):
        """Загрузка модели из конфиг файла"""
        config = self._load_config(config_path)
        model = self._build_model(config['architecture'])
        model.load_state_dict(torch.load(config['weights_path']))
        model.to(self.device).eval()
        return model, config

    def _build_model(self, architecture: dict):
        # Динамическое создание модели на основе конфига
        from torchvision import models
        
        if architecture['name'] == 'ResNet18':
            model = models.resnet18(pretrained=architecture['pretrained'])
            model.fc = torch.nn.Linear(
                model.fc.in_features, 
                architecture['num_classes']
            )
        return model

    def _load_config(self, path):
        with open(Path(settings.MODELS_DIR) / path) as f:
            return yaml.safe_load(f)