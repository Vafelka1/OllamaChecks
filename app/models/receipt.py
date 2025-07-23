from pydantic import BaseModel, Field
from typing import Optional


class ReceiptData(BaseModel):
    """Модель данных чека"""
    store_name: str = Field(..., description="Название магазина")
    total_amount: float = Field(..., gt=0, description="Общая сумма покупки")
    currency: Optional[str] = Field("RUB", description="Валюта")


class ReceiptAnalysisRequest(BaseModel):
    """Модель запроса анализа чека"""
    pass  # Изображение передается через multipart/form-data


class ReceiptAnalysisResponse(BaseModel):
    """Модель ответа анализа чека"""
    success: bool = Field(..., description="Успешность анализа")
    data: Optional[ReceiptData] = None
    error: Optional[str] = None


class TextQueryRequest(BaseModel):
    """Модель запроса для текстового общения с моделью"""
    message: str = Field(..., min_length=1, max_length=4000, description="Текстовое сообщение для модели")
    model: Optional[str] = Field("moondream:1.8b", description="Название модели Ollama для использования")
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0, description="Температура генерации (0.0 - детерминистично, 2.0 - креативно)")


class TextQueryResponse(BaseModel):
    """Модель ответа для текстового запроса"""
    success: bool = Field(..., description="Успешность обработки запроса")
    response: Optional[str] = Field(None, description="Ответ модели")
    model_used: Optional[str] = Field(None, description="Использованная модель")
    error: Optional[str] = Field(None, description="Сообщение об ошибке")


class ErrorResponse(BaseModel):
    """Модель ошибки"""
    detail: str = Field(..., description="Описание ошибки") 