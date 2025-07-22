"""
Общие зависимости и конфигурация для FastAPI приложения
"""

import logging
import io
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image

from app.services.ollama_service import OllamaService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальные константы
SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Инициализация сервисов
ollama_service = OllamaService()


async def validate_image(file: UploadFile) -> bytes:
    """
    Валидация загружаемого изображения
    
    Args:
        file: Загружаемый файл
        
    Returns:
        bytes: Байты изображения
        
    Raises:
        HTTPException: При ошибке валидации
    """
    # Проверка типа файла
    if file.content_type not in SUPPORTED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Неподдерживаемый формат файла. Поддерживаются: {', '.join(SUPPORTED_IMAGE_TYPES)}"
        )
    
    # Чтение файла
    content = await file.read()
    
    # Проверка размера файла
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Проверка, что файл действительно является изображением
    try:
        image = Image.open(io.BytesIO(content))
        image.verify()
    except Exception as e:
        logger.error(f"Ошибка при проверке изображения: {e}")
        raise HTTPException(
            status_code=400,
            detail="Поврежденное изображение или неподдерживаемый формат"
        )
    
    return content


def get_ollama_service() -> OllamaService:
    """
    Зависимость для получения сервиса Ollama
    
    Returns:
        OllamaService: Экземпляр сервиса
    """
    return ollama_service 