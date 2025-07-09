#!/usr/bin/env python
"""
Тестовый скрипт для проверки работы системы логирования.
Запуск: python test_logging.py
"""
import os
import sys
import django
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sms_analizator_service.settings')
django.setup()

from loguru import logger
from utils.logger_config import (
    setup_logging, 
    log_telegram_event, 
    log_webhook_request, 
    log_database_operation,
    get_api_logger,
    get_telegram_logger,
    get_webhook_logger,
    get_database_logger
)


def test_basic_logging():
    """Тестирование базового логирования."""
    print("🔧 Тестирование базового логирования...")
    
    logger.info("Тестовое INFO сообщение")
    logger.warning("Тестовое WARNING сообщение")
    logger.error("Тестовое ERROR сообщение")
    
    print("✅ Базовое логирование протестировано")


def test_api_logging():
    """Тестирование API логирования."""
    print("🌐 Тестирование API логирования...")
    
    api_logger = get_api_logger()
    api_logger.info("Тестовый API запрос")
    api_logger.warning("Тестовое API предупреждение")
    api_logger.error("Тестовая API ошибка")
    
    print("✅ API логирование протестировано")


def test_telegram_logging():
    """Тестирование Telegram логирования."""
    print("🤖 Тестирование Telegram логирования...")
    
    telegram_logger = get_telegram_logger()
    telegram_logger.info("Telegram бот запущен")
    
    # Тестирование специальной функции
    log_telegram_event(
        event_type="test_event",
        user_id="123456789",
        message="Тестовое событие",
        success=True
    )
    
    log_telegram_event(
        event_type="test_error",
        user_id="123456789",
        message="Тестовая ошибка",
        success=False
    )
    
    print("✅ Telegram логирование протестировано")


def test_webhook_logging():
    """Тестирование webhook логирования."""
    print("🔗 Тестирование webhook логирования...")
    
    webhook_logger = get_webhook_logger()
    webhook_logger.info("Webhook обработан")
    
    # Тестирование специальной функции
    test_data = {
        'result': {
            'caller_id': 'TEST_SENDER',
            'caller_did': '+71234567890',
            'text': 'Тестовое SMS сообщение'
        }
    }
    
    log_webhook_request(
        token="test_token_12345678",
        data=test_data,
        processing_result="Successfully processed"
    )
    
    print("✅ Webhook логирование протестировано")


def test_database_logging():
    """Тестирование логирования операций с БД."""
    print("🗄️ Тестирование логирования БД...")
    
    database_logger = get_database_logger()
    database_logger.info("Операция с БД выполнена")
    
    # Тестирование специальной функции
    log_database_operation(
        operation="CREATE",
        model="User",
        instance_id=1,
        user_id=1,
        success=True
    )
    
    log_database_operation(
        operation="DELETE",
        model="Rule",
        instance_id=5,
        user_id=1,
        success=False
    )
    
    print("✅ Логирование БД протестировано")


def check_log_files():
    """Проверка создания файлов логов."""
    print("📁 Проверка файлов логов...")
    
    log_dir = project_root / "logs"
    
    expected_files = [
        "app.log",
        "errors.log", 
        "api.log",
        "telegram_bot.log",
        "webhooks.log",
        "database.log"
    ]
    
    for file_name in expected_files:
        file_path = log_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"  ✅ {file_name} создан ({size} байт)")
        else:
            print(f"  ❌ {file_name} не найден")
    
    print("✅ Проверка файлов завершена")


def main():
    """Основная функция тестирования."""
    print("🚀 Запуск тестирования системы логирования SMS Анализатора\n")
    
    # Инициализация логирования
    setup_logging(project_root)
    print("✅ Логирование инициализировано\n")
    
    # Запуск тестов
    test_basic_logging()
    print()
    
    test_api_logging()
    print()
    
    test_telegram_logging()
    print()
    
    test_webhook_logging()
    print()
    
    test_database_logging()
    print()
    
    check_log_files()
    print()
    
    print("🎉 Тестирование завершено успешно!")
    print(f"📁 Логи сохранены в: {project_root / 'logs'}")
    print("\n💡 Проверьте содержимое файлов логов для убеждения в корректной работе.")


if __name__ == "__main__":
    main() 