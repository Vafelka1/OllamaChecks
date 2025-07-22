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


class ErrorResponse(BaseModel):
    """Модель ошибки"""
    detail: str = Field(..., description="Описание ошибки") 