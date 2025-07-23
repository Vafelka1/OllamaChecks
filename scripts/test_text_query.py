#!/usr/bin/env python3
"""
Тестовый скрипт для проверки ручки текстовых запросов к модели
"""

import asyncio
import httpx
import json
from typing import Dict, Any


class TextQueryTester:
    """Класс для тестирования ручки текстовых запросов"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        
    async def test_query(self, message: str, model: str = "moondream:1.8b", temperature: float = 0.7) -> Dict[str, Any]:
        """
        Тестирует отправку текстового запроса к модели
        
        Args:
            message: Текстовое сообщение
            model: Название модели
            temperature: Температура генерации
            
        Returns:
            Ответ API
        """
        payload = {
            "message": message,
            "model": model,
            "temperature": temperature
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                print(f"Отправка запроса: {message[:50]}...")
                print(f"Модель: {model}, Температура: {temperature}")
                
                response = await client.post(
                    f"{self.base_url}/query",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Успешный ответ:")
                    print(f"   Модель: {result.get('model_used')}")
                    print(f"   Ответ: {result.get('response', '')[:200]}...")
                    return result
                else:
                    print(f"❌ Ошибка {response.status_code}: {response.text}")
                    return {"error": response.text}
                    
        except Exception as e:
            print(f"❌ Исключение: {e}")
            return {"error": str(e)}
    
    async def test_health(self) -> bool:
        """Проверяет здоровье API"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    print("✅ API доступен")
                    return True
                else:
                    print(f"❌ API недоступен: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Ошибка подключения к API: {e}")
            return False


async def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование ручки текстовых запросов к модели\n")
    
    tester = TextQueryTester()
    
    # Проверка здоровья API
    print("1. Проверка доступности API...")
    if not await tester.test_health():
        print("API недоступен. Убедитесь, что сервер запущен.")
        return
    
    print("\n2. Тестирование текстовых запросов...\n")
    
    # Тестовые запросы
    test_cases = [
        {
            "message": "Привет! Как дела?",
            "model": "moondream:1.8b",
            "temperature": 0.7
        },
        {
            "message": "Расскажи короткую историю о коте",
            "model": "moondream:1.8b", 
            "temperature": 1.0
        },
        {
            "message": "Что такое машинное обучение? Объясни простыми словами.",
            "model": "moondream:1.8b",
            "temperature": 0.3
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Тест {i}:")
        await tester.test_query(**test_case)
        print("-" * 50)
    
    print("\n✅ Тестирование завершено!")


if __name__ == "__main__":
    asyncio.run(main()) 