# 📊 Руководство по системе логирования SMS Анализатора

## 🎯 Обзор системы

Система логирования построена на базе **loguru** и обеспечивает комплексное отслеживание всех операций в приложении с автоматической ротацией файлов и красивым форматированием.

## 📁 Структура логов

Все логи сохраняются в директории `logs/` в корне проекта:

```
logs/
├── app.log           # Общие операции приложения (INFO+)
├── errors.log        # Ошибки и исключения (WARNING+)
├── api.log           # HTTP запросы и API операции
├── telegram_bot.log  # События Telegram бота
├── webhooks.log      # Входящие webhook запросы
└── database.log      # Операции с базой данных
```

## 🔧 Конфигурация

### Автоматическая инициализация

Логирование автоматически инициализируется при запуске Django через `settings.py`:

```python
# В sms_analizator_service/settings.py
from utils.logger_config import setup_logging
setup_logging(BASE_DIR)
```

### Ротация файлов

- **Размер**: автоматическая ротация при достижении 10MB (обычные логи) / 5MB (ошибки)
- **Время**: хранение логов 30 дней (60 дней для ошибок)
- **Сжатие**: старые файлы автоматически сжимаются в .gz

## 🚀 Использование в коде

### Базовое логирование

```python
from loguru import logger

# Простые сообщения
logger.info("Операция выполнена успешно")
logger.warning("Предупреждение о потенциальной проблеме")
logger.error("Произошла ошибка")

# С дополнительным контекстом
logger.info("Пользователь {} выполнил действие {}", user_id, action)
```

### Специализированные логгеры

```python
from utils.logger_config import (
    get_api_logger,
    get_telegram_logger, 
    get_webhook_logger,
    get_database_logger
)

# API логирование
api_logger = get_api_logger()
api_logger.info("API запрос обработан")

# Telegram события
telegram_logger = get_telegram_logger()
telegram_logger.info("Сообщение отправлено в канал")
```

### Готовые функции логирования

#### HTTP запросы

```python
from utils.logger_config import log_request

def my_view(request):
    # Автоматическое логирование запроса
    log_request(request, 200, "Успешная обработка")
    return JsonResponse({'status': 'ok'})
```

#### Telegram события

```python
from utils.logger_config import log_telegram_event

# Успешное событие
log_telegram_event(
    event_type="user_registration",
    user_id="123456789", 
    message="Новый пользователь зарегистрирован",
    success=True
)

# Ошибка
log_telegram_event(
    event_type="message_send_failed",
    user_id="123456789",
    message="Не удалось отправить сообщение", 
    success=False
)
```

#### Webhook запросы

```python
from utils.logger_config import log_webhook_request

async def webhook_handler(request, token):
    data = json.loads(request.body)
    
    # Логирование входящего webhook
    log_webhook_request(token, data, "Processing started")
    
    # ... обработка ...
    
    log_webhook_request(token, data, "Successfully processed")
```

#### Операции с БД

```python
from utils.logger_config import log_database_operation

# Создание записи
log_database_operation(
    operation="CREATE",
    model="User", 
    instance_id=user.id,
    user_id=user.id,
    success=True
)

# Удаление записи
log_database_operation(
    operation="DELETE",
    model="Rule",
    instance_id=rule_id,
    user_id=request.user.id,
    success=True
)
```

## 🔄 Автоматическое логирование

### HTTP запросы (Middleware)

Все HTTP запросы автоматически логируются через `RequestLoggingMiddleware`:

- Метод и путь запроса
- ID пользователя или "Anonymous"
- IP адрес клиента
- Статус ответа
- Время обработки в миллисекундах

### Операции с БД (Signals)

Автоматическое логирование через Django signals для моделей:

- `User` - создание/обновление пользователей
- `Key` - добавление/удаление API ключей
- `NumbersService` - управление номерами телефонов
- `TelegramChats` - добавление/удаление каналов
- `Rules` - создание/удаление правил

## 📊 Мониторинг и анализ

### Просмотр логов в реальном времени

```bash
# Все логи
tail -f logs/app.log

# Только ошибки
tail -f logs/errors.log

# API запросы
tail -f logs/api.log

# Telegram события
tail -f logs/telegram_bot.log

# Webhook запросы
tail -f logs/webhooks.log
```

### Фильтрация логов

```bash
# Поиск по пользователю
grep "User: 123" logs/api.log

# Поиск ошибок за сегодня
grep "$(date +%Y-%m-%d)" logs/errors.log

# Webhook от конкретного отправителя
grep "SENDER_NAME" logs/webhooks.log

# Операции с определенной моделью
grep "CREATE User" logs/database.log
```

### Анализ производительности

```bash
# Медленные запросы (>1000ms)
grep "Response time: [0-9]\{4,\}" logs/api.log

# Количество запросов за час
grep "$(date +%Y-%m-%d\ %H)" logs/api.log | wc -l

# Статистика по статусам ответов
grep "Status: 4[0-9][0-9]" logs/api.log | wc -l  # 4xx ошибки
grep "Status: 5[0-9][0-9]" logs/api.log | wc -l  # 5xx ошибки
```

## 🐛 Отладка и диагностика

### Формат логов

```
2024-01-15 14:30:25.123 | INFO     | users_app.views:login_view:25 | Успешный вход пользователя: +71234567890 (ID: 1)
```

Структура:
- **Время**: точная временная метка
- **Уровень**: INFO, WARNING, ERROR, etc.
- **Источник**: модуль:функция:строка
- **Сообщение**: описание события

### Трассировка ошибок

Для ошибок автоматически включается backtrace и diagnose:

```python
try:
    risky_operation()
except Exception as e:
    logger.error("Ошибка в операции: {}", str(e))
    # Автоматически логируется полный стек вызовов
```

### Контекстное логирование

```python
# Добавление контекста к логгеру
contextual_logger = logger.bind(user_id=123, operation="sms_processing")
contextual_logger.info("SMS обработана")
# Результат: 2024-01-15 14:30:25.123 | INFO | SMS обработана | user_id=123 operation=sms_processing
```

## ⚙️ Настройка уровней логирования

### В режиме разработки (DEBUG=True)

- Консоль: DEBUG и выше
- Файлы: INFO и выше
- Включены backtrace и diagnose

### В продакшене (DEBUG=False)

- Консоль: INFO и выше
- Файлы: INFO и выше
- Backtrace только для ошибок

### Изменение уровней

```python
# В utils/logger_config.py можно изменить уровни:
logger.add(
    log_dir / "app.log",
    level="DEBUG",  # Изменить на DEBUG для более подробных логов
    # ...
)
```

## 🔒 Безопасность логирования

### Фильтрация чувствительных данных

```python
# Не логируем пароли и токены полностью
logger.info("API ключ добавлен: {}...", api_key[:8])
logger.info("Webhook токен: {}...", token[:8])

# Безопасное логирование номера телефона
phone_masked = phone[:3] + "***" + phone[-4:]
logger.info("SMS отправлена на номер: {}", phone_masked)
```

### Ротация и очистка

- Логи автоматически удаляются через 30-60 дней
- Старые файлы сжимаются для экономии места
- Настроены ограничения по размеру файлов

## 🧪 Тестирование

Запустите тестовый скрипт для проверки работы логирования:

```bash
python test_logging.py
```

Скрипт проверит:
- ✅ Создание всех типов логов
- ✅ Работу специализированных функций
- ✅ Создание файлов в нужной директории
- ✅ Корректность форматирования

## 📈 Рекомендации по использованию

### Уровни логирования

- **DEBUG**: Детальная отладочная информация (только в разработке)
- **INFO**: Обычные операции (вход пользователя, создание записей)
- **WARNING**: Потенциальные проблемы (неудачная валидация, повторные действия)
- **ERROR**: Ошибки, требующие внимания (исключения, сбои API)
- **CRITICAL**: Критические ошибки (сбой системы, потеря данных)

### Хорошие практики

```python
# ✅ Хорошо: информативные сообщения
logger.info("Пользователь {} создал правило для номера {}", user.phone, phone)

# ❌ Плохо: неинформативные сообщения  
logger.info("Операция выполнена")

# ✅ Хорошо: логирование с контекстом
logger.error("Ошибка отправки SMS: {} | Пользователь: {} | Номер: {}", 
            error, user.id, phone)

# ❌ Плохо: логирование без контекста
logger.error("Ошибка отправки SMS")
```

### Производительность

- Используйте ленивую подстановку строк: `logger.info("User: {}", user_id)`
- Избегайте тяжелых вычислений в сообщениях логов
- Фильтруйте логи по важности в продакшене

---

*Логирование настроено и готово к использованию! 🎉* 