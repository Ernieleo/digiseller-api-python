# Digiseller API Python

[![PyPI version](https://img.shields.io/pypi/v/digiseller-api-python.svg?cacheSeconds=3600)](https://pypi.org/project/digiseller-api-python)
[![PyPI Package Monthly Download](https://img.shields.io/pypi/dm/digiseller-api-python)](https://pypistats.org/packages/digiseller-api-python)
[![License](https://img.shields.io/github/license/Ernieleo/digiseller-api-python)](https://github.com/Ernieleo/digiseller-api-python/blob/master/LICENSE)
[![Test Status](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/test.yml/badge.svg)](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/test.yml)

English documentation available [here](./docs/README_en.md).

**Digiseller API Python** — это неофициальная Python-библиотека для взаимодействия с API Digiseller.

**Важное примечание**: Данный проект не связан с официальной командой разработчиков Digiseller и не является официальной библиотекой.  
Возможны неточности в некоторых запросах, поскольку комплексное тестирование не проводилось. Также, некоторые методы API, описанные в документации Digiseller, могут не соответствовать своему описанию на сайте.

Полную документацию API можно найти на [сайте Digiseller](https://my.digiseller.com/inside/api.asp).

## Установка

Установить пакет можно двумя способами:

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

### Пример кода
```python
from digiseller_api import DigisellerApi

# Создание экземпляра API-клиента
digiseller_api = DigisellerApi(seller_id="11155533", api_key="CA1SF69A000A46D00039F01Z11017V39")

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

### Описание использования
Этот пример показывает, как использовать `DigisellerApi` для получения данных, введенных покупателем при оформлении заказа.  
Функция `get_account_info_from_digiseller` выполняет запрос по уникальному коду и ищет данные по заданным названиям полей. Названия полей учитывают возможность различий в языке зависимых от выбранного пользователем на сайте.

## Разработка
Приветствуется вклад в развитие проекта!  
Если вы хотите помочь с поддержанием актуальности и дальнейшей разработкой, пожалуйста, следуйте официальным правилам API сервиса Digiseller и придерживайтесь общего стиля кода проекта.

Для внесения изменений создайте pull-реквест, и он будет рассмотрен.

## Запланировано 
В будущих планах создание документации для удобного и корректного использования.

## Полезные ссылки
- [Сайт Digiseller](https://my.digiseller.ru)  
- [Документация API Digiseller](https://my.digiseller.com/inside/api.asp)
- [Проект на PyPI](https://pypi.org/project/digiseller-api-python/)