#!/usr/bin/env python3
"""
Скрипт для тестирования Receipt Analyzer API
"""

import requests
import json
import sys
import time
from pathlib import Path


def test_health():
    """Тестирование health check endpoint"""
    print("🔍 Проверка состояния сервиса...")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Сервис работает: {data}")
            return True
        else:
            print(f"❌ Проблема с сервисом: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


def test_root():
    """Тестирование корневого endpoint"""
    print("🔍 Проверка корневого endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Корневой endpoint работает: {data}")
            return True
        else:
            print(f"❌ Проблема с корневым endpoint: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


def test_analyze_receipt(image_path: str):
    """Тестирование анализа чека"""
    print(f"🔍 Тестирование анализа чека: {image_path}")
    
    image_file = Path(image_path)
    if not image_file.exists():
        print(f"❌ Файл не найден: {image_path}")
        return False
    
    try:
        with open(image_file, 'rb') as f:
            files = {'image': (image_file.name, f, 'image/jpeg')}
            response = requests.post(
                "http://localhost:8000/analyze-receipt",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Анализ выполнен успешно:")
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return True
        else:
            print(f"❌ Ошибка анализа: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Детали ошибки: {error_data}")
            except:
                print(f"Ответ сервера: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")
        return False


def wait_for_service(max_attempts=30):
    """Ожидание запуска сервиса"""
    print("⏳ Ожидание запуска сервиса...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Сервис готов (попытка {attempt})")
                return True
        except:
            pass
        
        print(f"⏳ Попытка {attempt}/{max_attempts}: сервис еще не готов...")
        time.sleep(2)
    
    print("❌ Сервис не запустился в ожидаемое время")
    return False


def main():
    """Основная функция"""
    print("🧪 Тестирование Receipt Analyzer API")
    print("=" * 50)
    
    # Ожидание запуска сервиса
    if not wait_for_service():
        sys.exit(1)
    
    # Тестирование endpoints
    success = True
    
    success &= test_root()
    print()
    
    success &= test_health()
    print()
    
    # Тестирование анализа чека (если указан файл)
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        success &= test_analyze_receipt(image_path)
    else:
        print("ℹ️  Для тестирования анализа чека передайте путь к изображению:")
        print(f"   python {sys.argv[0]} /path/to/receipt.jpg")
    
    print()
    if success:
        print("🎉 Все тесты прошли успешно!")
    else:
        print("❌ Некоторые тесты не прошли")
        sys.exit(1)


if __name__ == "__main__":
    main() 