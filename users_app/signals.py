"""
Сигналы Django для логирования операций с базой данных.
"""
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from utils.logger_config import log_database_operation
from .models import User, Key, NumbersService, TelegramChats, Rules


@receiver(post_save, sender=User)
def log_user_operations(sender, instance, created, **kwargs):
    """Логирование операций с пользователями."""
    operation = "CREATE" if created else "UPDATE"
    log_database_operation(
        operation=operation,
        model="User",
        instance_id=instance.id,
        user_id=instance.id
    )


@receiver(post_save, sender=Key)
def log_key_operations(sender, instance, created, **kwargs):
    """Логирование операций с API ключами."""
    operation = "CREATE" if created else "UPDATE"
    log_database_operation(
        operation=operation,
        model="Key",
        instance_id=instance.id,
        user_id=instance.user.id
    )


@receiver(post_save, sender=NumbersService)
def log_numbers_service_operations(sender, instance, created, **kwargs):
    """Логирование операций с номерами телефонов."""
    operation = "CREATE" if created else "UPDATE"
    log_database_operation(
        operation=operation,
        model="NumbersService",
        instance_id=instance.id,
        user_id=instance.user.id
    )


@receiver(post_save, sender=TelegramChats)
def log_telegram_chats_operations(sender, instance, created, **kwargs):
    """Логирование операций с Telegram каналами."""
    operation = "CREATE" if created else "UPDATE"
    log_database_operation(
        operation=operation,
        model="TelegramChats",
        instance_id=instance.id,
        user_id=instance.user.id
    )


@receiver(post_save, sender=Rules)
def log_rules_operations(sender, instance, created, **kwargs):
    """Логирование операций с правилами переадресации."""
    operation = "CREATE" if created else "UPDATE"
    log_database_operation(
        operation=operation,
        model="Rules",
        instance_id=instance.id,
        user_id=instance.user.id
    )


@receiver(post_delete, sender=Key)
def log_key_deletion(sender, instance, **kwargs):
    """Логирование удаления API ключей."""
    log_database_operation(
        operation="DELETE",
        model="Key",
        instance_id=instance.id,
        user_id=instance.user.id
    )


@receiver(post_delete, sender=NumbersService)
def log_numbers_service_deletion(sender, instance, **kwargs):
    """Логирование удаления номеров телефонов."""
    log_database_operation(
        operation="DELETE",
        model="NumbersService",
        instance_id=instance.id,
        user_id=instance.user.id
    )


@receiver(post_delete, sender=TelegramChats)
def log_telegram_chats_deletion(sender, instance, **kwargs):
    """Логирование удаления Telegram каналов."""
    log_database_operation(
        operation="DELETE",
        model="TelegramChats",
        instance_id=instance.id,
        user_id=instance.user.id
    )


@receiver(post_delete, sender=Rules)
def log_rules_deletion(sender, instance, **kwargs):
    """Логирование удаления правил переадресации."""
    log_database_operation(
        operation="DELETE",
        model="Rules",
        instance_id=instance.id,
        user_id=instance.user.id
    )
