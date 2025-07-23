"""
Роутер для анализа чеков
"""

import logging
from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends

from app.models.receipt import ReceiptAnalysisResponse, ErrorResponse
from app.dependencies import validate_image, get_ollama_service
from app.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["receipt"]
)


@router.post(
    "/analyze-receipt", 
    response_model=ReceiptAnalysisResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка в запросе"},
        422: {"model": ErrorResponse, "description": "Не удалось распознать данные"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    },
    summary="Анализ чека",
    description="Анализирует изображение чека и извлекает название магазина, сумму покупки и валюту"
)
async def analyze_receipt(
    image: UploadFile = File(..., description="Изображение чека для анализа"),
    ollama_service: OllamaService = Depends(get_ollama_service)
):
    """
    Анализ чека и извлечение данных
    
    Args:
        image: Файл изображения чека (JPEG, PNG, WebP)
        ollama_service: Сервис для работы с Ollama
        
    Returns:
        ReceiptAnalysisResponse: Результат анализа с извлеченными данными
        
    Raises:
        HTTPException: При ошибках валидации или обработки
    """
    try:
        logger.info(f"Получен запрос на анализ чека: {image.filename}")
        
        # Валидация изображения
        image_bytes = await validate_image(image)
        logger.info(f"Изображение прошло валидацию, размер: {len(image_bytes)} байт")
        
        # Анализ с помощью Ollama
        receipt_data = await ollama_service.analyze_receipt(image_bytes)
        
        if receipt_data is None:
            logger.warning("Ollama не смог проанализировать чек")
            return ReceiptAnalysisResponse(
                success=False,
                data=None,
                error="Не удалось распознать данные чека. Попробуйте загрузить более четкое изображение."
            )
        
        logger.info(f"Анализ завершен успешно: {receipt_data}")
        return ReceiptAnalysisResponse(
            success=True,
            data=receipt_data,
            error=None
        )
        
    except HTTPException:
        # Переброс HTTP исключений
        raise
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка при анализе чека: {e}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при обработке запроса"
        )

 