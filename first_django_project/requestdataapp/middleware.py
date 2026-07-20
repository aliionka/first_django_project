from datetime import datetime, timedelta
from typing import Union, Dict

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.cache import cache
import logging
import threading  # Используем стандартный threading.Lock для атомарности
import time
from django.core.exceptions import PermissionDenied, SuspiciousOperation

logger = logging.getLogger(__name__)


class EnhancedRequestMiddleware:
    """
    Полноценный middleware с:
    - Добавлением user_agent
    - Измерением времени выполнения запроса
    - Добавлением ID запроса для трейсинга
    - Добавлением информации о клиенте (IP)
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._lock = threading.Lock()

        self.total_requests = 0
        self.slow_requests = 0

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # 1. Добавляем время начала запроса
        request.start_time = time.time()

        # 2. Добавляем User-Agent (безопасно)
        request.user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

        # 3. Добавляем IP клиента (с учетом прокси)
        request.client_ip = self._get_client_ip(request)

        # 4. Генерируем уникальный ID запроса (для логирования)
        request.request_id = self._generate_request_id()

        with self._lock:
            self.total_requests += 1

        # Логируем входящий запрос
        logger.info(
            f"[{request.request_id}] {request.method} {request.path} "
            f"from {request.client_ip} ({request.user_agent})"
        )

        try:
            response = self.get_response(request)
            elapsed = time.time() - request.start_time

            if elapsed > 1.0:
                with self._lock:
                    self.slow_requests += 1

                logger.warning(
                    f"[{request.request_id}] Slow request: {elapsed:.3f}s "
                    f"for {request.method} {request.path}"
                )

            # Добавляем заголовки в ответ (для отладки)
            response['X-Request-ID'] = request.request_id
            response['X-Execution-Time'] = f"{elapsed:.3f}s"

            # Логируем успешный ответ
            logger.info(
                f"[{request.request_id}] Response {response.status_code} "
                f"in {elapsed:.3f}s"
            )
            return response

        except Exception as e:
            elapsed = time.time() - request.start_time
            logger.error(
                f"[{request.request_id}] Error in {request.method} {request.path}: {e}",
                exc_info=True
            )
            raise

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Определяем реальный IP клиента, учитывая прокси"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', 'Unknown')
        return ip

    def _generate_request_id(self) -> str:
        """Генерируем уникальный ID для запроса"""
        import uuid
        return str(uuid.uuid4())[:8]

    def get_stats(self) -> dict:
        with self._lock:
            return {
                'total_requests': self.total_requests,
                'slow_requests': self.slow_requests,
                'slow_percentage': (
                    (self.slow_requests / self.total_requests * 100)
                    if self.total_requests > 0 else 0
                ),
            }


class CountRequestsMiddleware:
    """
    Счетчик запросов, ответов и исключений.
    С потокобезопасностью и обработкой ошибок.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self._lock = threading.Lock()

        # Счётчики
        self.requests_count = 0
        self.responses_count = 0
        self.exceptions_count = 0

    # def __call__(self, request: HttpRequest):
    #     self.requests_count += 1
    #     print("requests count", self.requests_count)
    #     response = self.get_response(request)
    #     self.responses_count += 1
    #     print("responses count", self.responses_count)
    #     return response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Атомарное увеличение счетчика запросов
        with self._lock:
            self.requests_count += 1

        try:
            response = self.get_response(request)

            # Атомарное увеличение счетчика ответов
            with self._lock:
                self.responses_count += 1

            return response

        except Exception as e:
            # Атомарное увеличение счетчика исключений
            with self._lock:
                self.exceptions_count += 1
            # Логируем ошибку
            logger.error(f"Exception in request to {request.path}: {e}")
            # Пробрасываем исключение дальше
            raise

    def get_stats(self):
        """Возвращает текущую статистику"""
        with self._lock:
            return {
                "requests": self.requests_count,
                "responses": self.responses_count,
                "exceptions": self.exceptions_count
            }


class ExceptionHandlingMiddleware:
    """Обработка исключений с JSON-ответом для API"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        return self.get_response(request)

    def process_exception(self, request: HttpRequest, exception: Exception) -> Union[HttpResponse, None]:
        is_api = (
                request.META.get('HTTP_ACCEPT') == 'application/json' or
                request.path.startswith('/api/')
        )

        if not is_api:
            return None

        status_code = 500
        error_code = 'internal_error'

        if isinstance(exception, PermissionDenied):
            status_code = 403
            error_code = 'forbidden'
        elif isinstance(exception, SuspiciousOperation):
            status_code = 400
            error_code = 'bad_request'

        return JsonResponse({
            'status': 'error',
            'code': error_code,
            'message': str(exception),
            'path': request.path,
        }, status=status_code)


class ThrottlingMiddleware:
    """
    Middleware для ограничения частоты запросов по IP.
    Хранит историю запросов в кэше.
    """
    RATE_LIMIT_MAX_REQUESTS = 10  # максимум запросов за окно
    RATE_LIMIT_WINDOW = 60  # секунд

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Получаем IP клиента
        ip = self._get_client_ip(request)

        if not ip:  # Если IP не определен, пропускаем запрос
            return self.get_response(request)

        try:
            # 2. Ключ для кэша
            cache_key = f'throttling_{ip}'

            # 3. Получаем историю запросов из кэша
            request_history = cache.get(cache_key, [])

            # 4. Очищаем старые записи (старше окна ограничения)
            current_time = datetime.now()
            window_start = current_time - timedelta(seconds=self.RATE_LIMIT_WINDOW)
            request_history = [t for t in request_history if t > window_start]

            # 5. Проверяем лимит
            if len(request_history) >= self.RATE_LIMIT_MAX_REQUESTS:
                # Превышение лимита - возвращаем ошибку 429
                logger.warning(f'Throttling: IP {ip} exceeded rate limit '
                               f'({len(request_history)} requests in {self.RATE_LIMIT_WINDOW}s)')
                return HttpResponse(
                    'Too many requests. Please wait and try again later',
                    status=429,
                    headers={
                        'Retry-After': str(self.RATE_LIMIT_WINDOW),
                        'X-RateLimit-Limit': str(self.RATE_LIMIT_MAX_REQUESTS),
                    }
                )

            # 6. Добавляем текущий запрос в историю
            request_history.append(current_time)
            # Сохраняем в кэше на время окна ограничения
            cache.set(cache_key, request_history, timeout=self.RATE_LIMIT_WINDOW)

        except Exception as e:
            # Если кэш недоступен - логируем и пропускаем запрос
            logger.error(f"Throttling cache error for IP {ip}: {e}")
            return self.get_response(request)

        # 7. Продолжаем обработку запроса
        response = self.get_response(request)

        # 8. Добавляем информационные заголовки в ответ
        response['X-RateLimit-Limit'] = str(self.RATE_LIMIT_MAX_REQUESTS)
        response['X-RateLimit-Remaining'] = str(self.RATE_LIMIT_MAX_REQUESTS - len(request_history))
        response['X-RateLimit-Reset'] = str(int(current_time.timestamp() + self.RATE_LIMIT_WINDOW))

        return response

    def _get_client_ip(self, request):
        """Получение реального IP клиента с учетом прокси"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Если через прокси, берем первый IP (самый удаленный клиент)
            ip = x_forwarded_for.split(',')[0].strip()

        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
