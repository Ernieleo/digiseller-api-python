class DigisellerError(Exception):
    """Базовый класс для всех ошибок, связанных с Digiseller API."""
    pass


class DigisellerTimeoutError(DigisellerError):
    """Ошибка тайм-аута при запросе к API Digiseller."""
    pass


class DigisellerInvalidResponseError(DigisellerError):
    """Ошибка при получении некорректного ответа от API Digiseller."""
    pass


class DigisellerHTTPError(DigisellerError):
    """Ошибка HTTP с указанием кода статуса."""
    def __init__(self, status_code, message):
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code

class DigisellerUnavailableError(DigisellerError):
    """Ошибка когда Digiseller недоступен"""
    pass

class DigisellerAPIAuthError(DigisellerError):
    """Ошибка когда недостаточно прав доступа"""
    pass


class DigisellerProxyError(DigisellerError):
    """Ошибка связанная с использованием прокси"""
    pass