import json
import base64
import httpx
from typing import Optional, Dict, Any
import logging
from pathlib import Path

from app.models.receipt import ReceiptData

logger = logging.getLogger(__name__)


class OllamaService:
    """Сервис для работы с Ollama API"""
    
    def __init__(self, base_url: str = "http://ollama:11434"):
        self.base_url = base_url
        self.model = "moondream:1.8b"  # Легкая vision модель для анализа изображений
        self.max_retries = 3
        
    async def analyze_receipt(self, image_bytes: bytes) -> Optional[ReceiptData]:
        """
        Анализирует чек с помощью Ollama
        
        Args:
            image_bytes: Байты изображения чека
            
        Returns:
            ReceiptData или None при ошибке
        """
        # Кодируем изображение в base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Специальный промпт для vision модели Moondream
        vision_prompt = """Проанализируй это изображение чека и извлеки следующую информацию:
1. Название магазина или организации
2. Общую сумму покупки (итог к оплате)
3. Валюту (обычно RUB для российских чеков)

Ответь СТРОГО в формате JSON:
{
    "store_name": "название магазина",
    "total_amount": числовое_значение,
    "currency": "RUB"
}

Если информация не найдена, используй null для соответствующих полей."""
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Попытка анализа чека {attempt + 1}/{self.max_retries}")
                
                # Формируем запрос к Ollama для vision модели
                payload = {
                    "model": self.model,
                    "prompt": vision_prompt,
                    "images": [image_base64],
                    "stream": False,
                    "format": "json"
                }
                
                async with httpx.AsyncClient(timeout=300.0) as client:
                    response = await client.post(
                        f"{self.base_url}/api/generate",
                        json=payload
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    response_text = result.get("response", "")
                    
                    logger.info(f"Ответ от Ollama: {response_text}")
                    
                    # Парсим JSON ответ
                    try:
                        parsed_data = json.loads(response_text)
                        receipt_data = ReceiptData(**parsed_data)
                        logger.info(f"Успешно распознаны данные: {receipt_data}")
                        return receipt_data
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.warning(f"Ошибка парсинга JSON (попытка {attempt + 1}): {e}")
                        if attempt == self.max_retries - 1:
                            # Последняя попытка - пробуем с более строгим промптом
                            vision_prompt = self._get_strict_vision_prompt()
                        continue
                        
            except httpx.HTTPError as e:
                logger.error(f"HTTP ошибка при запросе к Ollama: {e}")
                if attempt == self.max_retries - 1:
                    break
                    
            except Exception as e:
                logger.error(f"Неожиданная ошибка: {e}")
                if attempt == self.max_retries - 1:
                    break
                    
        logger.error("Не удалось проанализировать чек после всех попыток")
        return None
    
    def _get_strict_vision_prompt(self) -> str:
        """Возвращает более строгий промпт для vision модели"""
        return """Внимательно изучи изображение чека. Найди:
- Название магазина (вверху чека)
- Итоговую сумму (обычно внизу, "ИТОГО", "К ДОПЛАТЕ", "СУММА")
- Валюту (RUB, руб.)

ОТВЕТЬ ТОЛЬКО JSON:
{"store_name": "название", "total_amount": число, "currency": "RUB"}

Примеры:
{"store_name": "Магнит", "total_amount": 1250.50, "currency": "RUB"}
{"store_name": null, "total_amount": null, "currency": "RUB"}"""

    async def health_check(self) -> bool:
        """Проверка доступности Ollama"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False 