"""
Middleware для автоматического логирования HTTP запросов.
"""
import time
from loguru import logger
from utils.logger_config import log_request


class RequestLoggingMiddleware:
    """
    Middleware для логирования всех HTTP запросов и ответов.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Запоминаем время начала обработки запроса
        start_time = time.time()
        
        # Обрабатываем запрос
        response = self.get_response(request)
        
        # Вычисляем время обработки
        process_time = round((time.time() - start_time) * 1000, 2)  # в миллисекундах
        
        # Логируем запрос
        extra_info = f"Response time: {process_time}ms"
        if hasattr(response, 'status_code'):
            log_request(request, response.status_code, extra_info)
        else:
            log_request(request, None, extra_info)
            
        return response

    def process_exception(self, request, exception):
        """
        Логирование исключений.
        """
        logger.error(f"Исключение при обработке запроса {request.method} {request.path}: {exception}")
        log_request(request, 500, f"Exception: {str(exception)}")
        return None 