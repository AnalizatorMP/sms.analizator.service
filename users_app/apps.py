from django.apps import AppConfig


class UsersAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users_app'
    
    def ready(self):
        """Подключение сигналов для логирования."""
        import users_app.signals