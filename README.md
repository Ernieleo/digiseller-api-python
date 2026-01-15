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
Список методов библиотеки и их соответствие официальному API можно найти в [MAPPING.md](docs/MAPPING.md).   
Методы API для покупателей из блока 'Оплата' недоступны в библиотеке.

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
# Вы можете указать timeout (по умолчанию 60) и proxy (по умолчанию None)
digiseller_api = DigisellerApi(
    seller_id="11155533", 
    api_key="ZA1SG0YDA46DV0Z39F01Z11017V39",
    timeout=120,
    proxy="http://user:pass@127.0.0.1:8080" 
)


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

Для работы этого примера требуется установить библиотеку `Pillow` (`pip install Pillow`).

```python
from digiseller_api_python import DigisellerApi

from PIL import Image
from io import BytesIO

# Инициализируем клиент (даже если метод не требует авторизации, архитектура библиотеки требует экземпляр)
# Для публичных методов можно передать любые или пустые seller_id/api_key, 
# но лучше использовать реальные, чтобы избежать путаницы.
digiseller_api = DigisellerApi(seller_id="YOUR_SELLER_ID", api_key="YOUR_API_KEY")


image = digiseller_api.get_main_img(id_d=4470041, maxlength=400, w=200, h=150, crop=False)

# Открываем изображение из байтов напрямую
image_bytes = image.encode() if isinstance(image, str) else image
image = Image.open(BytesIO(image_bytes))
image.show()
```

В данном примере представлено взаимодействие с функцией [получения основного изображения товара](https://my.digiseller.com/inside/api_catgoods.asp#fast_image).

### Возвращаемые данные

- **JSON (`application/json`)**: Возвращается как **словарь Python**.
- **XML (`application/xml` или `text/xml`)**: Возвращается как **строка** XML.
- **Изображение (`image/*`)**: Возвращается как **байтовый объект**.
- **Текст (`text/plain` и другие текстовые форматы)**: Возвращается как **строка**.
- **StatusCode: 204 (NoContent)** → {"success": True}

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

| Исключение                       | Описание                                                  |
|----------------------------------|-----------------------------------------------------------|
| `DigisellerError`                | Базовое исключение                                        |
| `DigisellerTimeoutError`         | Тайм-аут при запросе к API                                |
| `DigisellerInvalidResponseError` | Ответ от API не соответствует ожиданиям (по документации) |
| `DigisellerHTTPError`            | Ошибка HTTP (например, 400, 500 и т.д.)                   |
| `DigisellerUnavailableError`     | Digiseller загружается, но не работает или обновляется    |
| `DigisellerAPIAuthError`         | Недостаточно прав. Проверьте права доступа с ключом API   |
| `DigisellerProxyError`           | Ошибка при подключении через прокси                       |
---

Вы можете использовать исключения для логирования, отладки

## Разработка
Приветствуется вклад в развитие проекта!  
Если вы хотите помочь с поддержанием актуальности и дальнейшей разработкой, пожалуйста, следуйте официальным правилам API сервиса Digiseller и придерживайтесь общего стиля кода проекта.

Для внесения изменений создайте форк и последующий pull-реквест, и он будет рассмотрен.

Если обнаружите ошибку, связанную с работой кода, пожалуйста, создайте **Issue** в репозитории — это поможет оперативно её исправить.

---

#### Обращение к разработчикам Digiseller.
Просьба — навести порядок в документации. В текущем виде она содержит множество несоответствий фактической работе API: ошибки в описании параметров, различающееся написание одних и тех же полей в рамках одного метода, неполные пояснения и явные следы ручного оформления каждой страницы.
Пора переходить на современные стандарты: OpenAPI, корректно описанные схемы и удобный Swagger-интерфейс. Это значительно упростит взаимодействие с API и снизит количество ошибок у интеграторов.

## Запланировано 
В будущих планах создание документации для удобного и корректного использования.
- [x] Добавить все функции API
- [x] Дополнительный пример использования в Python
- [x] Добавить дополнительные отсутствующие функции
- [x] Полная документация методов (см. [MAPPING.md](docs/MAPPING.md))
- [x] Добавить оставшиеся функции (за исключением)
- [x] Добавить возможность использования Proxy

## Полезные ссылки
- [Проект на PyPI](https://pypi.org/project/digiseller-api-python/)
- [Сайт Digiseller](https://my.digiseller.ru)  
- [Документация API Digiseller](https://my.digiseller.com/inside/api.asp)
- [Хостинг с хорошими ценами](https://bill.yacolo.net/billmgr?from=58735) (**Промокод:** yacolo#58735)
