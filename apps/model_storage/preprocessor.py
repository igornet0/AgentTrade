import torch
from torchvision import transforms

class DataPreprocessor:
    def __init__(self, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=mean, std=std)
        ])

    def __call__(self, data):
        # data может быть PIL.Image или numpy array
        return self.transform(data).unsqueeze(0)  # Добавляем batch dimension