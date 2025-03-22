import os
import unittest
from dotenv import load_dotenv

from digiseller_api_python import DigisellerApi, DigisellerError, DigisellerTimeoutError, DigisellerInvalidResponseError, DigisellerHTTPError

load_dotenv()

class TestDigisellerApiCore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seller_id = os.getenv("SELLER_ID") or "dummy_id"
        cls.api_key = os.getenv("API_KEY") or "dummy_key"
        cls.api = DigisellerApi(seller_id=cls.seller_id, api_key=cls.api_key)

    def test_exceptions_structure(self):
        """Проверка иерархии исключений"""
        for exc in [
            DigisellerTimeoutError,
            DigisellerInvalidResponseError,
            DigisellerHTTPError,
        ]:
            with self.subTest(exception=exc.__name__):
                self.assertTrue(
                    issubclass(exc, DigisellerError),
                    msg=f"{exc.__name__} не наследует DigisellerError",
                )

    def test_get_token(self):
        """Проверка получения токена перед релизом"""

        try:
            token = self.api.get_token()
        except DigisellerInvalidResponseError as e:
            self.fail(f"Токен не получен. Ошибка в ответе Digiseller API: {e}")
        except DigisellerError as e:
            self.fail(f"API Digiseller вернул ошибку: {e}")
        except Exception as e:
            self.fail(f"Ошибка: {e}")

        # Проверяем, что токен корректный
        self.assertIsInstance(token, str, "❌ Токен должен быть строкой")
        self.assertTrue(len(token) > 10, "❌ Токен слишком короткий или пустой")

        print(f"✅ Токен получен ({len(token)} символов)")

    # def test_class_and_methods_have_docstrings(self):
    #     """Проверка документации в классе и его методах"""
    #     self.assertIsNotNone(
    #         DigisellerApi.__doc__,
    #         msg="Класс DigisellerApi должен содержать docstring",
    #     )
    #     for attr in dir(self.api):
    #         if not attr.startswith("_"):
    #             obj = getattr(self.api, attr)
    #             if callable(obj):
    #                 with self.subTest(method=attr):
    #                     self.assertIsNotNone(
    #                         obj.__doc__,
    #                         msg=f"Метод `{attr}` должен иметь docstring",
    #                     )

    def test_smoke_instantiation(self):
        """Smoke-тест: просто инициализация класса"""
        self.assertIsInstance(self.api, DigisellerApi)


if __name__ == "__main__":
    unittest.main()
