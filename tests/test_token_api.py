import os
import unittest

from digiseller_api.base_api import DigisellerApi


class TestDigisellerApiToken(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.seller_id = os.getenv("SELLER_ID")
        cls.api_key = os.getenv("API_KEY")

        assert cls.seller_id is not None, "SELLER_ID не настроен в переменных окружения"
        assert cls.api_key is not None, "API_KEY не настроен в переменных окружения"

        cls.api = DigisellerApi(seller_id=cls.seller_id, api_key=cls.api_key)

    def test_get_token(self):
        response = self.api._token_response()

        self.assertIsInstance(response, dict, "Ответ не является словарем")
        self.assertEqual(response.get("retval"), 0, "Получен неверный retval")

        token = response.get("token")
        self.assertIsInstance(token, str, "Поле token отсутствует или не является строкой")

        self.assertEqual(response.get("seller_id"), int(self.seller_id), "seller_id не совпадает")

        self.assertIsInstance(response.get("valid_thru"), str, "valid_thru не является строкой")

        print("Токен успешно получен и все поля проверены на корректность.")


# Запуск тестов
if __name__ == '__main__':
    unittest.main()
