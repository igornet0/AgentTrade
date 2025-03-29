from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict
import asyncio
import json

# Модель запроса
class NewsRequest(BaseModel):
    text: str
    max_tokens: int = 500  # Добавляем параметры для гибкости
    temperature: float = 0.3

# Модель ответа
class CryptoImpactResponse(BaseModel):
    crypto: Dict[str, float]

async def run_async(func, *args):
    """Вспомогательная функция для запуска синхронных операций в пуле потоков"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)

@app.post("/analyze", response_model=CryptoImpactResponse)
async def analyze_news(news_request: NewsRequest):
    """
    Анализирует текст новости и возвращает оценки влияния на криптовалюты
    
    Параметры:
    - text: Текст новости для анализа
    - max_tokens: Максимальное количество токенов для генерации ответа
    - temperature: Параметр температуры для модели (0.0-1.0)
    """
    try:
        # Запускаем синхронную операцию в отдельном потоке
        result = await run_async(
            analyze_news_impact,
            news_request.text,
            news_request.max_tokens,
            news_request.temperature
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке запроса: {str(e)}"
        )

# Модифицированная версия вашей функции с параметрами
def analyze_news_impact(news_text: str, max_tokens: int = 500, temperature: float = 0.3) -> dict:
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": """You are a financial analyst. Analyze news text and identify mentioned cryptocurrencies. 
                    For each cryptocurrency, return impact score (-100 to 100) where:
                    - -100 = strong negative impact
                    - 0 = neutral/no impact
                    - 100 = strong positive impact
                    Return ONLY valid JSON format: {"crypto": {"ticker": score}}"""
                },
                {
                    "role": "user",
                    "content": f"News text: {news_text}"
                }
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.9,
            frequency_penalty=0.5,
            response_format={"type": "json_object"},
            stream=False
        )
        
        # Парсинг и валидация ответа
        result = json.loads(response.choices[0].message.content)
        if not isinstance(result.get("crypto"), dict):
            raise ValueError("Некорректный формат ответа от модели")
            
        return result
    except json.JSONDecodeError:
        raise ValueError("Ошибка декодирования JSON-ответа")
    except Exception as e:
        raise RuntimeError(f"Ошибка в работе модели: {str(e)}")

# Добавляем обработку CORS (если нужно)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)