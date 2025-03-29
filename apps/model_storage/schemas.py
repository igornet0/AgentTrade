from pydantic import BaseModel

class PredictionRequest(BaseModel):
    model_name: str
    input_data: list  # или специфичные для модели данные

class PredictionResponse(BaseModel):
    predictions: list
    confidence: list[float]
    model_version: str

class ModelInfo(BaseModel):
    name: str
    input_shape: tuple
    device: str
    status: str