<p align="center">
  <img src="https://i.ibb.co/hyTLSDZ/digiseller-logo.png" alt="Digiseller API Python" width="80%">
</p>

[![PyPI version](https://img.shields.io/pypi/v/digiseller-api-python.svg?cacheSeconds=3600)](https://pypi.org/project/digiseller-api-python)
[![PyPI Package Monthly Download](https://img.shields.io/pypi/dm/digiseller-api-python)](https://pypistats.org/packages/digiseller-api-python)
[![License](https://img.shields.io/github/license/Ernieleo/digiseller-api-python)](https://github.com/Ernieleo/digiseller-api-python/blob/master/LICENSE)
[![Test Status](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/test.yml/badge.svg)](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/release_pypi.yml)

English documentation available [here](https://github.com/Ernieleo/digiseller-api-python/blob/master/docs/README_en.md).

**Digiseller API Python** — это неофициальная Python-библиотека для взаимодействия с API Digiseller.

**Важное примечание**: Данный проект не связан с официальной командой разработчиков Digiseller и не является официальной библиотекой.  
Возможны неточности в некоторых запросах, поскольку комплексное тестирование не проводилось, так как некоторые методы API, описанные в документации Digiseller, могут не соответствовать своему описанию.

Полную документацию API можно найти на [сайте Digiseller](https://my.digiseller.com/inside/api.asp).  
Методы API для покупателей из блока 'Оплата' недоступны в библиотеке.

## ⚠️ Изменение способа импорта (с версии 3.0.0)

Начиная с версии **3.0.0**, библиотека использует новую структуру.  
Импорт должен выполняться из `digiseller_api_python`, а не `digiseller_api`.

### Было (до 3.0.0):
```python
from digiseller_api import DigisellerApi
```
### Стало (с 3.0.0):
```python
from digiseller_api_python import DigisellerApi
```

---

## Установка

### С использованием PyPI:
```sh
pip install digiseller-api-python
```

### Установка из репозитория GitHub:
```sh
pip3 install git+https://github.com/Ernieleo/digiseller-api-python.git
```

## Пример использования

Чтобы использовать Digiseller API, вам понадобятся `API ключ` и `ID продавца`:

- Получите **API ключ** [здесь](https://my.digiseller.com/inside/api_keys.asp).
- Получите **ID продавца** [здесь](https://my.digiseller.com/).

Не забывайте - ваш API ключ должен оставаться в безопасности, не публикуйте его в интернете.

### Пример кода

```python
from digiseller_api_python import DigisellerApi

# Создание экземпляра API-клиента
digiseller_api = DigisellerApi(seller_id="11155533", api_key="ZA1SG0YDA46DV0Z39F01Z11017V39")


# Пример функции для получения данных, указанных пользователем при заказе, по уникальному коду
def get_account_info_from_digiseller(unique_code):
    email, password = None, None
    try:
        # Выполняем запрос
        data = digiseller_api.unique_code(unique_code)

        # Извлекаем необходимые данные
        for option in data.get("options", []):
            if option["name"] in ["Почта аккаунта ChatGPT", "ChatGPT account email"]:
                email = option["value"]
            elif option["name"] in ["Пароль аккаунта ChatGPT", "ChatGPT account password"]:
                password = option["value"]

        return email, password
    except Exception as e:
        # Обработка исключений
        print(f"Ошибка: {e}")
        return None, None


# Использование функции для получения информации
unique_code = "ВАШ_УНИКАЛЬНЫЙ_КОД"
email, password = get_account_info_from_digiseller(unique_code)
print("Email:", email)
print("Password:", password)
```

Этот пример показывает, как использовать `DigisellerApi` для получения данных, введенных покупателем при оформлении заказа.  
Функция `get_account_info_from_digiseller` выполняет запрос по уникальному коду и ищет данные по заданным названиям полей. Названия полей учитывают возможность различий в языке зависимых от выбранного пользователем на сайте.

### Дополнительный пример

```python
from digiseller_api_python import DigisellerApi

from PIL import Image
from io import BytesIO

image = DigisellerApi.get_main_img(id_d=4470041, maxlength=400)
# Открываем изображение из байтов напрямую
image_bytes = image.encode() if isinstance(image, str) else image
image = Image.open(BytesIO(image_bytes))
image.show()
```

В данном примере представлено взаимодействие с функцией [получения основного изображения товара](https://my.digiseller.com/inside/api_catgoods.asp#fast_image), вызов происходит без использования данных продавца и создания экземпляра API-клиента.

### Возвращаемые данные

- **JSON (`application/json`)**: Возвращается как **словарь Python**.
- **XML (`application/xml` или `text/xml`)**: Возвращается как **строка** XML.
- **Изображение (`image/*`)**: Возвращается как **байтовый объект**.
- **Текст (`text/plain` и другие текстовые форматы)**: Возвращается как **строка**.
- **Другие типы**: Возвращается **статус-код** ответа.

## Обработка исключений

Библиотека предоставляет собственные классы исключений, позволяющие точно обрабатывать ошибки при работе.

### Базовое исключение

```python
from digiseller_api_python import DigisellerError
```

Все исключения библиотеки наследуются от `DigisellerError`, поэтому можно перехватывать как конкретные, так и общие ошибки:

```python
try:
    digiseller_api.get_token()
except DigisellerError as e:
    print(f"Ошибка Digiseller API: {e}")
```

---

### Доступные исключения

| Исключение                       | Описание                                |
|----------------------------------|-----------------------------------------|
| `DigisellerError`                | Базовое исключение                      |
| `DigisellerTimeoutError`         | Тайм-аут при запросе к API              |
| `DigisellerInvalidResponseError` | Ответ от API не соответствует ожиданиям |
| `DigisellerHTTPError`            | Ошибка HTTP (например, 400, 500 и т.д.) |

---

Вы можете использовать исключения для логирования, отладки

## Разработка
Приветствуется вклад в развитие проекта!  
Если вы хотите помочь с поддержанием актуальности и дальнейшей разработкой, пожалуйста, следуйте официальным правилам API сервиса Digiseller и придерживайтесь общего стиля кода проекта.

Для внесения изменений создайте форк и последующий pull-реквест, и он будет рассмотрен.

## Запланировано 
В будущих планах создание документации для удобного и корректного использования.
- [x] Добавить все функции API
- [x] Дополнительный пример использования в Python
- [x] Добавить дополнительные отсутствующие функции
- [ ] Полная документация методов (в разработке)
- [x] Добавить оставшиеся функции (за исключением)

## Полезные ссылки
- [Проект на PyPI](https://pypi.org/project/digiseller-api-python/)
- [Сайт Digiseller](https://my.digiseller.ru)  
- [Документация API Digiseller](https://my.digiseller.com/inside/api.asp)
- [Хостинг с хорошими ценами](https://bill.yacolo.net/billmgr?from=58735) (**Промокод:** yacolo#58735)
