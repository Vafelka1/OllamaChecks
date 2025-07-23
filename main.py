"""
Receipt Analyzer API

Микросервис для анализа чеков с помощью Ollama + Gemma
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from app.routers import health, receipt, chat

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Создание FastAPI приложения
app = FastAPI(
    title="Receipt Analyzer API",
    description="Микросервис для анализа чеков с помощью Ollama + Gemma",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Подключение роутеров
app.include_router(health.router)
app.include_router(receipt.router)
app.include_router(chat.router)


# Глобальные обработчики исключений
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Обработчик HTTP исключений"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Глобальный обработчик исключений"""
    logger.error(f"Необработанная ошибка: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 