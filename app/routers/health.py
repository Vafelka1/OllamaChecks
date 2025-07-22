"""
Роутер для проверки состояния сервиса
"""

import logging
from fastapi import APIRouter, Depends

from app.dependencies import get_ollama_service
from app.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["health"]
)


@router.get("/")
async def root():
    """Корневой endpoint с информацией о сервисе"""
    return {
        "message": "Receipt Analyzer API",
        "version": "1.0.0",
        "status": "running",
        "description": "Микросервис для анализа чеков с помощью Ollama + Gemma"
    }


@router.get("/health")
async def health_check(
    ollama_service: OllamaService = Depends(get_ollama_service)
):
    """
    Проверка состояния сервиса и его компонентов
    
    Returns:
        dict: Статус сервиса и его зависимостей
    """
    logger.info("Проверка состояния сервиса")
    
    # Проверка доступности Ollama
    ollama_status = await ollama_service.health_check()
    
    overall_status = "healthy" if ollama_status else "degraded"
    
    return {
        "status": overall_status,
        "components": {
            "ollama": "available" if ollama_status else "unavailable",
            "api": "running"
        },
        "version": "1.0.0",
        "timestamp": "2024-01-01T00:00:00Z"  # В реальном приложении используйте datetime.now()
    } 