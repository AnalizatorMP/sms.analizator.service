"""
Конфигурация логирования для SMS Анализатора.
Использует loguru для структурированного логирования с ротацией файлов.
"""
import os
import sys
from pathlib import Path
from loguru import logger

from django.conf import settings


def setup_logging():
    """
    Настройка системы логирования с использованием loguru.
    
    Конфигурирует:
    - Различные уровни логирования для разных компонентов
    - Ротацию файлов по размеру и времени
    - Форматирование сообщений
    - Разделение логов по типам (общие, ошибки, API, бот)
    """
    
    # Удаляем стандартный обработчик loguru
    logger.remove()
    
    # Определяем директорию для логов
    log_dir = Path(settings.BASE_DIR) / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Формат для логов
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Формат для файлов (без цветов)
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # Консольный вывод (только в режиме отладки)
    if settings.DEBUG:
        logger.add(
            sys.stderr,
            format=log_format,
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
    else:
        logger.add(
            sys.stderr,
            format=log_format,
            level="INFO",
            colorize=True
        )
    
    # Общий лог файл (все сообщения INFO и выше)
    logger.add(
        log_dir / "app.log",
        format=file_format,
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="gz",
        backtrace=False,
        diagnose=False
    )
    
    # Лог ошибок (WARNING и выше)
    logger.add(
        log_dir / "errors.log",
        format=file_format,
        level="WARNING",
        rotation="5 MB",
        retention="60 days",
        compression="gz",
        backtrace=True,
        diagnose=True
    )
    
    # Лог API запросов
    logger.add(
        log_dir / "api.log",
        format=file_format,
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="gz",
        filter=lambda record: "api" in record["extra"]
    )
    
    # Лог Telegram бота
    logger.add(
        log_dir / "telegram_bot.log",
        format=file_format,
        level="INFO",
        rotation="5 MB",
        retention="30 days",
        compression="gz",
        filter=lambda record: "telegram" in record["extra"]
    )
    
    # Лог webhook запросов
    logger.add(
        log_dir / "webhooks.log",
        format=file_format,
        level="INFO",
        rotation="10 MB",
        retention="30 days",
        compression="gz",
        filter=lambda record: "webhook" in record["extra"]
    )
    
    # Лог операций с базой данных
    logger.add(
        log_dir / "database.log",
        format=file_format,
        level="INFO",
        rotation="5 MB",
        retention="30 days",
        compression="gz",
        filter=lambda record: "database" in record["extra"]
    )
    
    logger.info("Система логирования инициализирована")


def get_logger(name: str = None, **extra_context):
    """
    Получить настроенный логгер с дополнительным контекстом.
    
    Args:
        name: Имя логгера (обычно __name__)
        **extra_context: Дополнительный контекст для фильтрации логов
    
    Returns:
        Настроенный логгер
    """
    if extra_context:
        return logger.bind(**extra_context)
    return logger


# Предустановленные логгеры для разных компонентов
api_logger = get_logger(api=True)
telegram_logger = get_logger(telegram=True)
webhook_logger = get_logger(webhook=True)
database_logger = get_logger(database=True)


def log_request(request, response_status=None, extra_info=None):
    """
    Логирование HTTP запросов.
    
    Args:
        request: Django request объект
        response_status: Статус ответа
        extra_info: Дополнительная информация
    """
    user_info = f"User: {request.user.id if request.user.is_authenticated else 'Anonymous'}"
    ip_info = f"IP: {request.META.get('REMOTE_ADDR', 'Unknown')}"
    method_path = f"{request.method} {request.path}"
    
    log_message = f"{method_path} | {user_info} | {ip_info}"
    
    if response_status:
        log_message += f" | Status: {response_status}"
    
    if extra_info:
        log_message += f" | {extra_info}"
    
    if response_status and response_status >= 400:
        api_logger.warning(log_message)
    else:
        api_logger.info(log_message)


def log_telegram_event(event_type: str, user_id: str = None, message: str = None, success: bool = True):
    """
    Логирование событий Telegram бота.
    
    Args:
        event_type: Тип события (start, contact, registration, etc.)
        user_id: ID пользователя Telegram
        message: Дополнительное сообщение
        success: Успешность операции
    """
    log_message = f"Event: {event_type}"
    
    if user_id:
        log_message += f" | User ID: {user_id}"
    
    if message:
        log_message += f" | {message}"
    
    if success:
        telegram_logger.info(log_message)
    else:
        telegram_logger.error(log_message)


def log_webhook_request(token: str, data: dict, processing_result: str = None):
    """
    Логирование webhook запросов.
    
    Args:
        token: Токен пользователя
        data: Данные запроса
        processing_result: Результат обработки
    """
    log_message = f"Webhook request | Token: {token[:8]}..."
    
    if 'result' in data:
        result = data['result']
        caller_id = result.get('caller_id', 'Unknown')
        caller_did = result.get('caller_did', 'Unknown')
        log_message += f" | From: {caller_id} | To: {caller_did}"
    
    if processing_result:
        log_message += f" | Result: {processing_result}"
    
    webhook_logger.info(log_message)


def log_database_operation(operation: str, model: str, instance_id=None, user_id=None, success: bool = True):
    """
    Логирование операций с базой данных.
    
    Args:
        operation: Тип операции (CREATE, UPDATE, DELETE)
        model: Название модели
        instance_id: ID экземпляра
        user_id: ID пользователя
        success: Успешность операции
    """
    log_message = f"{operation} {model}"
    
    if instance_id:
        log_message += f" | ID: {instance_id}"
    
    if user_id:
        log_message += f" | User: {user_id}"
    
    if success:
        database_logger.info(log_message)
    else:
        database_logger.error(log_message) 