"""
Роутер для текстовых запросов к модели
"""

import logging
from fastapi import APIRouter, HTTPException, Depends

from app.models.receipt import TextQueryRequest, TextQueryResponse, ErrorResponse
from app.dependencies import get_ollama_service
from app.services.ollama_service import OllamaService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["Chat"]
)


@router.post(
    "/query",
    response_model=TextQueryResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Ошибка в запросе"},
        422: {"model": ErrorResponse, "description": "Ошибка валидации данных"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    },
    summary="Текстовый запрос к модели",
    description="Отправляет текстовое сообщение к языковой модели Ollama и возвращает ответ"
)
async def query_model(
    request: TextQueryRequest,
    ollama_service: OllamaService = Depends(get_ollama_service)
):
    """
    Отправка текстового запроса к языковой модели
    
    Args:
        request: Запрос с текстовым сообщением и параметрами
        ollama_service: Сервис для работы с Ollama
        
    Returns:
        TextQueryResponse: Ответ модели с результатом обработки
        
    Raises:
        HTTPException: При ошибках валидации или обработки
    """
    try:
        logger.info(f"Получен текстовый запрос к модели {request.model}: {request.message[:100]}...")
        
        # Отправляем запрос к модели
        model_response = await ollama_service.query_text(
            message=request.message,
            model=request.model,
            temperature=request.temperature
        )
        
        if model_response is None:
            logger.warning(f"Модель {request.model} не смогла обработать запрос")
            return TextQueryResponse(
                success=False,
                response=None,
                model_used=request.model,
                error="Не удалось получить ответ от модели. Проверьте доступность модели или попробуйте позже."
            )
        
        logger.info(f"Запрос успешно обработан моделью {request.model}")
        return TextQueryResponse(
            success=True,
            response=model_response,
            model_used=request.model,
            error=None
        )
        
    except HTTPException:
        # Переброс HTTP исключений
        raise
        
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке текстового запроса: {e}")
        raise HTTPException(
            status_code=500,
            detail="Внутренняя ошибка сервера при обработке запроса"
        ) 