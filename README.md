# 📄 Receipt Analyzer - Микросервис анализа чеков

Микросервис для автоматического извлечения данных из изображений чеков с использованием Ollama (Moondream vision) и FastAPI.

## ✨ Возможности

- 🔍 Извлечение названия магазина и суммы покупки из чеков
- 🤖 Использование Ollama с vision моделью Moondream для распознавания
- 📋 Структурированный JSON-ответ с валидацией
- 🐳 Полная контейнеризация с Docker Compose
- 🔄 Автоматические повторные попытки при ошибках распознавания
- 📊 Health check endpoints
- ⚡ Оптимизация для GPU с ограниченной VRAM

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- NVIDIA GPU с минимум 1.5GB VRAM (поддерживает CUDA)
- Минимум 4GB RAM

### 1. Клонирование и запуск

```bash
# Клонирование репозитория
git clone <repository-url>
cd receipt-analyzer

# Запуск сервисов
docker-compose up -d

# Проверка статуса
docker-compose ps
```

### 2. Настройка Moondream vision модели

```powershell
# Windows PowerShell
./scripts/setup_model.ps1
```

### 3. Тестирование API

```bash
# Проверка состояния сервиса
curl http://localhost:8000/health

# Анализ чека (замените путь на ваш файл)
curl -X POST "http://localhost:8000/analyze-receipt" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "image=@/path/to/receipt.jpg"
```

## 🔧 Решение проблем с GPU

### Проблема: Ollama не использует GPU

**Симптомы:**
```
layers.offload=0  # 0 слоев в GPU
memory.available="[1.5 GiB]" 
memory.required.full="1.8 GiB"  # Moondream требует меньше памяти
```

**Решение:**

1. **Использование легкой vision модели** - Moondream 1.8b специально для анализа изображений
2. **Настройка переменных окружения в docker-compose.yml:**
   ```yaml
   environment:
     - OLLAMA_GPU_OVERHEAD=128M
     - OLLAMA_FLASH_ATTENTION=true
     - OLLAMA_NUM_GPU_LAYERS=20  # Большинство слоев в GPU
     - CUDA_VISIBLE_DEVICES=0
   ```

3. **Запуск скрипта настройки:**
   ```powershell
   # Windows
   ./scripts/setup_model.ps1
   ```

4. **Перезапуск сервисов:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Проверка статуса GPU

```bash
# Проверка загруженных моделей
docker exec ollama ollama ps

# Логи для диагностики
docker logs ollama | grep -E "(offload|GPU|CUDA)"
```

**Ожидаемый результат после исправления:**
```
layers.offload=20  # Большинство слоев в GPU
memory.gpu.total="~700MB"   # GPU память 
memory.cpu.total="~1.1GB"   # CPU память
```

## 📖 API Документация

### Endpoints

#### `GET /`
Корневой endpoint с информацией о сервисе.

#### `GET /health`
Проверка состояния сервиса и доступности Ollama.

#### `POST /analyze-receipt`
Анализ изображения чека.

**Параметры:**
- `image` (file): Изображение чека (JPEG, PNG, WebP)

**Ответ:**
```json
{
  "success": true,
  "data": {
    "store_name": "Магнит",
    "total_amount": 1250.50,
    "currency": "RUB"
  },
  "error": null
}
```

### Автоматическая документация

После запуска сервиса доступна по адресам:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔧 Конфигурация

### Переменные окружения

**Для Receipt Service:**
- `OLLAMA_BASE_URL` - URL Ollama API (по умолчанию: http://ollama:11434)

**Для Ollama (Moondream vision модель):**
- `OLLAMA_GPU_OVERHEAD=128M` - Резерв памяти GPU (меньше для легкой модели)
- `OLLAMA_FLASH_ATTENTION=true` - Уменьшение использования памяти
- `OLLAMA_NUM_GPU_LAYERS=20` - Количество слоев в GPU (из ~24 всего)
- `CUDA_VISIBLE_DEVICES=0` - Выбор GPU устройства

### Настройки модели

В файле `app/services/ollama_service.py`:
- `model` - используемая модель (moondream:1.8b специализированная vision модель)
- `max_retries` - количество повторных попыток (по умолчанию: 3)
- `timeout` - таймаут запросов (300 секунд для GPU инференса)

## 🏗️ Архитектура

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client        │───▶│  FastAPI Service │───▶│ Ollama Moondream│
│                 │    │                  │    │   Vision Model  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Pydantic Models  │
                       │   Validation     │
                       └──────────────────┘
```

### Компоненты

1. **FastAPI сервис** (`main.py`)
   - Обработка HTTP запросов
   - Валидация изображений
   - Обработка ошибок

2. **Ollama Service** (`app/services/ollama_service.py`)
   - Интеграция с Ollama API
   - Форматирование промптов
   - Повторные попытки с увеличенными таймаутами

3. **Pydantic модели** (`app/models/receipt.py`)
   - Валидация данных
   - Схемы API

4. **Vision модель оптимизация** (`docker-compose.yml`)
   - Настройки NVIDIA GPU для Moondream
   - Переменные окружения для CUDA
   - Оптимизация памяти для компактной модели

## 🛠️ Разработка

### Локальная разработка

```bash
# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt

# Запуск в режиме разработки
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Структура проекта

```
receipt-analyzer/
├── app/
│   ├── models/
│   │   ├── __init__.py
│   │   └── receipt.py          # Pydantic модели
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── health.py           # Роутер для health check
│   │   └── receipt.py          # Роутер для анализа чеков
│   ├── services/
│   │   ├── __init__.py
│   │   └── ollama_service.py   # Сервис для Ollama API
│   ├── dependencies.py         # Общие зависимости и валидация
│   └── __init__.py
├── scripts/
│   ├── setup_model.ps1         # Настройка модели (Windows)
│   └── test_api.py             # Скрипт тестирования
├── main.py                     # Главное FastAPI приложение
├── requirements.txt            # Python зависимости
├── Dockerfile                  # Docker образ
├── docker-compose.yml          # Оркестрация сервисов (с GPU)
├── .gitignore                  # Git исключения
├── .dockerignore              # Docker исключения
└── README.md                  # Документация
```

## 🐛 Устранение неполадок

### Ollama не отвечает

```bash
# Проверка логов Ollama
docker logs ollama

# Перезапуск сервиса
docker-compose restart ollama
```

### Модель не найдена

```bash
# Загрузка модели
docker exec -it ollama ollama pull moondream:1.8b

# Проверка доступных моделей
docker exec -it ollama ollama list
```

### GPU не используется

```bash
# Проверка статуса GPU в контейнере
docker exec ollama nvidia-smi

# Проверка переменных окружения
docker exec ollama printenv | grep -E "(CUDA|OLLAMA)"

# Логи загрузки модели
docker logs ollama | grep -E "(layers|offload|GPU)"
```

### Ошибки распознавания

- Убедитесь, что изображение четкое и хорошо освещенное
- Проверьте, что текст на чеке читаемый
- Попробуйте другой формат изображения
- Проверьте статус GPU и загрузку модели

### Таймауты

- Увеличены таймауты до 300 секунд для GPU инференса
- Используется Flash Attention для ускорения
- Moondream vision модель: компактная и специализированная для изображений

## 📝 Лицензия

MIT License

## 🤝 Вклад в проект

1. Fork проекта
2. Создайте feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit изменений (`git commit -m 'Add some AmazingFeature'`)
4. Push в branch (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request 