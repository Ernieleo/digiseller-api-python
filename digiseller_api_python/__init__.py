""" digiseller-api python package created by Ernieleo. Version 1.1"""

import requests
import hashlib
import time
import json

from requests import Response


class Api:
    URL = 'https://api.digiseller.ru/api/'

    def __init__(self, seller_id, api_key):
        """
        API key получить на https://my.digiseller.com/inside/api_keys.asp
        Seller ID получить на главной https://my.digiseller.com/inside/my_info.asp

        Args:
            seller_id (str): ID продавца (Seller_ID).
            api_key (str): API Ключ доступа.

        Raises:
            ValueError: Если seller_id или api_key не переданы или имеют недопустимое значение.
        """

        if not isinstance(seller_id, str) or not seller_id:
            raise ValueError("Необходимо передать в API корректный 'seller_id'.\nПолучить идентификатор продавца можно в блоке 'Контактные данные' на my.digiseller.com")

        if not isinstance(api_key, str) or not api_key:
            raise ValueError("Необходимо передать в API корректный 'api_key'.\nПолучить ключ с назначением прав доступа, в разделе API на my.digiseller.com")

        self.session = requests.Session()
        self.seller_id = int(seller_id)
        self.api_key = api_key
        self.token_expiration = 0
        self.token = None

    def __get_token(self):
        current_time = int(time.time())
        if self.token is None or current_time >= self.token_expiration:
            sign = hashlib.sha256((self.api_key + str(current_time)).encode()).hexdigest()
            data = {
                "seller_id": self.seller_id,
                "timestamp": current_time,
                "sign": sign
            }
            response = self.session.post(self.URL + 'apilogin', json=data)
            if response.status_code == 200:
                response_data = response.json()
                self.token = response_data.get('token')
                self.token_expiration = current_time + 5400  # Жизнь токена - 1.5 часа [По докам 2, но на всякий]
            else:
                raise ValueError("Не удалось получить токен.")
        return self.token

    """ Общие методы """

    def __request(self, method, uri_path, **options):
        """
        Отправка запросов на сервер.

        Args:
            method (str): HTTP-метод, который будет использоваться для запроса.
            uri_path (str): API, на который будет отправлен запрос.
            options (dict): Дополнительные опции по запросу.

        Returns:
            mixed: Ответ от сервера.

        Raises:
            Exception: Если во время запроса возникает ошибка.
        """
        current_time = int(time.time())
        if self.token is None or current_time >= self.token_expiration:
            token = self.__get_token()
            if 'params' in options:
                options['params']['token'] = token
            elif 'json' in options:
                options['json']['token'] = token
            else:
                uri_path += f'?token={token}'

        headers = {'Accept': 'application/json; charset=UTF-8'}
        if 'files' not in options:
            headers['Content-Type'] = 'application/json'
        if 'headers' in options:
            headers.update(options.pop('headers'))
        options['headers'] = headers

        response = self.session.request(method, self.URL + uri_path, **options)
        try:
            if response.status_code == 200 and response.text:
                data = response.json()
                if 'retval' in data and data['retval'] != 0:
                    error_message = f"Ошибка в API: '{data.get('retdesc', 'Неизвестная ошибка Digiseller API')}'"
                    if 'errors' in data:
                        for error in data['errors']:
                            message = next((msg['value'] for msg in error['message'] if msg['locale'] == 'ru-RU'),
                                           next((msg['value'] for msg in error['message'] if msg['locale'] == 'en-US'), "Неизвестная ошибка"))
                            error_message += f". Код ошибки: '{error['code']}'. Причина ошибки: '{message}'."
                    raise ValueError(error_message)
                return data
            elif response.status_code == 200 and not response.text:
                return {"message": "Запрос выполнен успешно"}
            else:
                raise Exception(f'Ошибка при обработке ответа! HTTP Код состояния: {response.status_code}, содержимое: {response.text}')
        except json.decoder.JSONDecodeError:
            raise ValueError(f"Ошибка декодирования JSON: Код HTTP '{response.status_code}'\nТело ответа: '{response.text}'")

    def unique_code(self, unique_code: str):
        """
        Поиск и проверка платежа по уникальному коду.

        Args:
            unique_code (int): 	уникальный 16-ти значный код, который покупатель получает после оплаты.

        Returns:
            dict: Ответ от сервера в формате JSON.
                URL INFO: "https://my.digiseller.com/inside/api_general.asp#searchuniquecode"

        """

        return self.__request('GET', f'purchases/unique-code/{unique_code}', params={"token": self.token})

    def purchase_info(self, invoice_id: int):
        """
        Информация о продаже по номеру заказа

        Args:
            invoice_id (int): номер заказа в системе Digiseller	ID.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_general.asp#purchase_info"
        """

        return self.__request('GET', f'/purchase/info/{invoice_id}', params={"token": self.token})

    """ Статистика """

    def seller_last_sales(self, group: bool, top: int):
        """
        Список последних продаж.

        Args:
            group (bool): группировка по товару, true (по умолчанию) | false
            top (int, optional): количество записей ID, по умолчанию 1000

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_statistics.asp#last_sales"
        """

        params = {
            "token": self.token,
            "seller_id": self.seller_id,
            "group": group,
            "top": top
        }

        return self.__request('GET', f'seller-last-sales', params=params)

    def seller_sells_statistic(self, product_ids: list, date_start: str, date_finish: str, returned: int, page: int, rows: int):
        """
        Статистика продаж.

        Args:
            product_ids (dict, optional): Идентификаторы товаров. Массив целых чисел; если не указать, возвращается статистика по всем товарам.
            date_start (str): Начальная дата. Формат данных: 'yyyy-MM-dd HH:mm:ss'. Часовой пояс: Московское время UTC+03:00.
            date_finish (str): Конечная дата. Формат данных: 'yyyy-MM-dd HH:mm:ss'. Часовой пояс: Московское время UTC+03:00.
            returned (int): Возвраты. 0 - Включить возвраты; 1 - Исключить возвраты; 2 - Только возвраты.
            page(int): Номер страницы.
            rows(int): Количество записей на странице. Не более 2000.


        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_statistics.asp#statisticsells"
        """
        data = {
            "product_ids": product_ids,
            "date_start": date_start,
            "date_finish": date_finish,
            "returned": returned,
            "page": page,
            "rows": rows
        }

        return self.__request('POST', f'seller-sells/v2', params={"token": self.token}, json=data)

    def agent_sales_statistic(self, product_ids: list, date_start: str, date_finish: str, returned: int, page: int, rows: int):
        """
        Статистика продаж в роли агента.

        Args:
            product_ids (dict, optional): Идентификаторы товаров. Массив целых чисел; если не указать, возвращается статистика по всем товарам.
            date_start (str): Начальная дата. Формат данных: 'yyyy-MM-dd HH:mm:ss'. Часовой пояс: Московское время UTC+03:00.
            date_finish (str): Конечная дата. Формат данных: 'yyyy-MM-dd HH:mm:ss'. Часовой пояс: Московское время UTC+03:00.
            returned (int): Возвраты. 0 - Включить возвраты; 1 - Исключить возвраты; 2 - Только возвраты.
            page(int): Номер страницы.
            rows(int): Количество записей на странице. Не более 2000.

        Returns:
            Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_statistics.asp#statistics_agent_sales"
        """
        data = {
            "product_ids": product_ids,
            "date_start": date_start,
            "date_finish": date_finish,
            "returned": returned,
            "page": page,
            "rows": rows
        }

        return self.__request('POST', f'agent-sales/v2', params={"token": self.token}, json=data)

    """ Товары и категории """

    def categories_list(self, category_id: int, lang: str):
        """
        Список категорий (каталог).

        Args:
            category_id (int): ID категории. 0 - выбирается все дерево каталога.
            lang (int): язык Отображения информации	ru-RU (по умолчанию) или en-US.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_catgoods.asp#categories"
        """

        params = {
            "seller_id": self.seller_id,
            "category_id": category_id,
            "lang": lang
        }

        return self.__request("GET", f"categories?", params=params)

    def shop_products(self, category_id: int, page: int, rows: int, order: str,
                      currency: str, lang: str):
        """
        Список товаров из категории.

        Args:
            category_id (int): ID категории	ID если указать:
                    0 - отбираются товары добавленные на главную страницу
                    -1 - отбираются товары со знаком "скидка"
                    -2 - отбираются товары со знаком "новинка"
                    -3 - отбираются товары со знаком "популярный"
            page (int): Номер страницы (если не указывать номер страницы, то отображается первая страница) ID.
            rows (int): Количество строк на странице ID (значение по умолчанию 20, max. 500).
            order (str): Способ сортировки товаров (если не указывать, то расположение товаров как в "Моем магазине"):
                    name - сортировка по названию,
                    nameDESC - сортировка по названию (обрат.),
                    price - сортировка по цене,
                    priceDESC - сортировка по цене (обрат.)
            currency (str): Тип валюты для отображения стоимости товара	USD, RUR, EUR или UAH.
            lang (str): Язык отображения информации	ru-RU (по умолчанию) или en-US.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_catgoods.asp#products"
        """

        params = {
            "seller_id": self.seller_id,
            "category_id": category_id,
            "page": page,
            "rows": rows,
            "order": order,
            "currency": currency,
            "lang": lang
        }

        return self.__request("GET", f"shop/products", params=params)

    def products_description(self, ids: list, lang: str):
        """
        Быстрое получение описаний товаров по списку ID.

        Args:
            ids (list): идентификаторы товаров [1,2,3] (не более 2000).
            lang (str): язык отображения информации	ru-RU (по умолчанию) или en-US.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_catgoods.asp#products_list"
        """

        data = {
            "ids": ids,
            "lang": lang,
            "token": self.token
        }

        return self.__request('POST', 'products/list', json=data)

    def product_description(self, product_id: int, seller_id: int, partner_uid: str, currency: str, lang: str, owner: int):
        """
        Описание товара.

        Args:
            product_id (int): идентификатор товара.
            seller_id (int, optional): необязательный параметр, указывайте если используете корзину. ID продавца товара или свой ID (если товар принадлежит вам или вы добавили его в свой магазин).
            partner_uid (str, optional): партнерский UID (для учета индивидуальных отчислений).
            currency (str): валюта	USD (по умолчанию) или RUB | EUR | UAH.
            lang (str): язык отображения информации	ru-RU (по умолчанию) или en-US.
            owner (int, optional): при передаче значения в ответе будут присутствовать все способы оплаты, поддерживаемые торговой площадкой (если товар размещен на торговой площадке).

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_catgoods.asp#product_info"
        """

        params = {
            "seller_id": seller_id,
            "partner_uid": partner_uid,
            "currency": currency,
            "lang": lang,
            "token": self.token,
            "owner": owner
        }

        return self.__request('GET', f'products/{product_id}/data', params=params)

    def products_price_calc(self, product_id: int, options: str, currency: str, amount: int, unit_cnt: int, count: int):
        """
        Получение цены с учетом входящих значений параметров и/или количества товара.

        Args:
            product_id (int): идентификатор товара	ID.
            options (str): перечисление пар идентификатор-значение, для значимых параметров (влияющих на цену) пара идентификатор-значение указываются в виде {optionId}:{valueId},
                    например ?options[]=28532:41541&options[]=28530:41534.
            currency (str): валюта	трехзначный код метода оплаты (WMR | WMZ | ... ).
            amount (int): стоимость, исходя из указанного количества единиц товара.
            unit_cnt (int): количество товара с нефиксированной ценой	параметр является обязательным для товара с нефиксированной ценой.
            count (int): количество товара с фиксированной ценой.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_catgoods.asp#products_price_calc"
        """

        params = {
            "product_id": product_id,
            "options": options,
            "currency": currency,
            "amount": amount,
            "unit_cnt": unit_cnt,
            "count": count
        }

        return self.__request('GET', f'products/price/calc', params=params)

    def product_reviews(self, seller_id: int, product_id: int, type_: str, owner_id: int, page: int,
                        rows: int, lang: str):
        """
        Отзывы о товарах.
        Без указания ID товара - получить все отзывы.

        Args:
            seller_id (int): ID продавца.
            product_id (int, optional): ID товара.
            type_ (int): тип получаемого отзыва.
                good - положительные
                bad - отрицательные
                all - все отзывы
            owner_id (str): идентификатор торговой площадки.
                0 - собственный магазин
                1 - Plati.Market (ru)
                1271 - GGSell
                9295 - WMCenter.net
            page (str): номер страницы (если не указывать номер страницы, то отображается первая страница) ID.
            rows (int): количество строк на странице ID.
            lang (int): язык отображения информации	ru-RU (по умолчанию) или en-US.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_catgoods.asp#reviews"
        """

        params = {
            "seller_id": seller_id,
            "product_id": product_id,
            "type": type_,
            "owner_id": owner_id,
            "page": page,
            "rows": rows,
            "lang": lang
        }

        return self.__request('GET', f'reviews', params=params)

    def seller_goods(self, seller_id: int, order_col: str, order_dir: str, rows: int, page: int, currency: str, lang: str, show_hidden: int):
        """
        Получаем товары продавца.

        Args:
            seller_id (int): ID продавца.
            order_col (str): поле сортировки:
                "name" - название
                "price" - цена
                "cntsell" - количество продаж (по умолчанию)
                "cntreturn" - количество возвратов
                "cntgoodresponses" - количество положительных отзывов
                "cntbadresponses" - количество отрицательных отзывов
            order_dir (str): порядок сортировки:
                "asc" - по возрастанию
                "desc" - по убыванию (по умолчанию)
            rows (int): количество на странице (не более 2000).
            page (int): номер страницы.
            currency (str): тип валюты для отображения цены товара.
            lang (str): язык отображения информации.
            show_hidden (int): скрытые товары.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_catgoods.asp#seller-goods"
        """

        data = {
            "id_seller": seller_id,
            "order_col": order_col,
            "order_dir": order_dir,
            "rows": rows,
            "page": page,
            "currency": currency,
            "lang": lang,
            "show_hidden": show_hidden,
            "token": self.token
        }

        return self.__request('POST', f'seller-goods', params={"token": self.token}, json=data)

    """
    SKIP: Скидка по товару, Поиск по товарам, Быстрое получение основного изображения товара.
    """

    def product_clone(self, product_id: int, count: int, categories: bool, notify: bool, discounts: bool, options: bool, comissions: bool, gallery: bool):
        """
        Создание копии описания товара (клонирование без содержимого).

        Args:
            product_id (int): ID товара.
            count (int): Количество создаваемых копий.
            categories (bool): Созданные копии разместить в тех же категориях, что и оригинальный товар.
            notify (bool): Копировать настройки уведомлений.
            discounts (bool): Копировать настройки скидок.
            options (bool): Копировать настройки дополнительных параметров.
            comissions (bool): Копировать настройки компенсаций.
            gallery (bool): Копировать изображения и видео.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_catgoods.asp#copyproduct"
        """
        data = {
            "count": count,
            "categories": categories,
            "notify": notify,
            "discounts": discounts,
            "options": options,
            "comissions": comissions,
            "gallery": gallery
        }

        return self.__request('POST', f'product/clone/{product_id}', params={"token": self.token}, json=data)

    def agents_offer(self, seller_id: int, product_name: str, product_id: int, only_in_stock: bool,
                     only_individual: bool, page: int, count: int):
        """
        Список товаров продавца с индивидуальным предложением.

        Args:
            seller_id (int): ID продавца.
            product_name (str, optional): Название товара.
            product_id (int, optional): ID товара. ID.
            only_in_stock (bool): Только товары в наличии. По умолчанию: false.
            only_individual (bool): Только с индивидуальными комиссионными. По умолчанию: false.
            page (int): Номер страницы.
            count (int): Количество на странице (1 - 100).

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_catgoods.asp#goodswithoffer"
        """

        params = {
            "sellerId": seller_id,
            "productName": product_name,
            "productId": product_id,
            "onlyInStock": only_in_stock,
            "onlyIndividual": only_individual,
            "page": page,
            "count": count,
            "token": self.token
        }

        return self.__request('GET', f'agents/offer', params=params)

    """ Создание и редактирование товаров """

    def product_create_uniquefixed(self, data: dict):
        """
        Создание товара типа 'Уникальный товар с фиксированной ценой'.

        Args:
            data (dict): Тело, которое необходимо отправить в запросе.
            {
                "contenttype_": "text",
                "name": [
                    {
                        "locale": "ru-RU",
                        "value": "Тестовый продукт №1"
                    },
                    {
                        "locale": "en-US",
                        "value": "Test product №1"
                    }
                ],
                "price": {
                    "price": 725,
                    "currency": "RUB"
                },
                "comission_partner": 15,
                "categories": [
                    {
                        "owner": 0,
                        "category_id": 7074
                    },
                    {
                        "owner": 1,
                        "category_id": 18162
                    }
                ],
                "bonus": {
                    "enabled": false,
                    "percent": 5
                },
                "guarantee": {
                    "enabled": true,
                    "value": 5
                },
                "description": [
                    {
                        "locale": "ru-RU",
                        "value": "Тестовое описание"
                    },
                    {
                        "locale": "en-US",
                        "value": "Test description"
                    }
                ],
                "add_info": [
                    {
                        "locale": "ru-RU",
                        "value": "Тестовая дополнительная информация"
                    },
                    {
                        "locale": "en-US",
                        "value": "Test additional information"
                    }
                ],
                "address_required": false,
                "verify_code": {
                    "auto_verify": true,
                    "verify_url": "https://example.com/verify"
                },
                "preorder": {
                    "enabled": true,
                    "delivery_date": "2018-10-10"
                }
                "instruction": {
                    "type": "text",
                    "locales": [
                        {
                            "locale": "ru-RU",
                            "value": "Русская инструкция"
                        },
                        {
                            "locale": "en-US",
                            "value": "English instruction"
                        }
                    ]
                },
                "present_product_id": 123321
            }


        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#createuniquefixed"
        """
        return self.__request("POST", f'product/create/uniquefixed', params={"token": self.token}, json=data)

    def product_create_uniqueunfixed(self, data: dict):
        """
        Создание товара типа 'Уникальный товар с нефиксированной ценой'.

        Args:
            data (dict): Тело, которое необходимо отправить в запросе.
                {
                    "contenttype_": "digisellercode",
                    "name": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовый продукт №1"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test product №1"
                        }
                    ],
                    "prices": {
                        "price": 250,
                        "unit_quantity": 1000000,
                        "currency": "RUB,
                        "unit_name": "Gold"
                    },
                    "comission_partner": 15,
                    "categories": [
                        {
                            "owner": 0,
                            "category_id": 7074
                        },
                        {
                            "owner": 1,
                            "category_id": 18162
                        }
                    ],
                    "bonus": {
                        "enabled": false,
                        "percent": 5
                    },
                    "guarantee": {
                        "enabled": true,
                        "value": 5
                    },
                    "description": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовое описание"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test description"
                        }
                    ],
                    "add_info": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовая дополнительная информация"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test additional information"
                        }
                    ],
                    "address_required": false,
                    "verify_code": {
                        "auto_verify": true,
                        "verify_url": "https://example.com/verify",
                        "parameters": ["test"],
                        "redirect_to": "https://example.com/failurl"
                    },
                    "discounts": [
                        {
                            "unit_for_discount": 1.0,
                            "discount": 1
                        },
                        {
                            "unit_for_discount": 1.0,
                            "discount": 1
                        }
                    ],
                    "limitations": {
                        "type": "sample string 1",
                        "only_integer": true,
                        "limitations": [
                          1,
                          2
                        ]
                    },
                    "instruction": {
                        "type": "text",
                        "locales": [
                            {
                                "locale": "ru-RU",
                                "value": "Русская инструкция"
                            },
                            {
                                "locale": "en-US",
                                "value": "English instruction"
                            }
                        ]
                    },
                    "present_product_id": 123321
                }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#createuniqueunfixed"
        """
        return self.__request('POST', f'product/create/uniqueunfixed', params={"token": self.token}, json=data)

    def product_create_book(self, data: dict):
        """
        Создание товара типа 'Электронная книга'.

        Args:
            data (dict): Тело, которое необходимо отправить в запросе.
                {
                    "contenttype_": "text",
                    "name": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовый продукт №1"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test product №1"
                        }
                    ],
                    "price": {
                        "price": 725,
                        "currency": "RUB"
                    },
                    "comission_partner": 15,
                    "categories": [
                        {
                            "owner": 0,
                            "category_id": 7074
                        },
                        {
                            "owner": 1,
                            "category_id": 18162
                        }
                    ],
                    "bonus": {
                        "enabled": false,
                        "percent": 5
                    },
                    "guarantee": {
                        "enabled": true,
                        "value": 5
                    },
                    "description": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовое описание"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test description"
                        }
                    ],
                    "add_info": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовая дополнительная информация"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test additional information"
                        }
                    ],
                    "address_required": false,
                    "trial_url": "http://localhost",
                    "instruction": {
                        "type": "text",
                        "locales": [
                            {
                                "locale": "ru-RU",
                                "value": "Русская инструкция"
                            },
                            {
                                "locale": "en-US",
                                "value": "English instruction"
                            }
                        ]
                    },
                    "present_product_id": 123321
                }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#createbook"
        """
        return self.__request('POST', f'product/create/book', params={"token": self.token}, json=data)

    def product_create_software(self, data: dict):
        """
        Создание товара типа 'Программное обеспечение'.

        Args:
            data (dict): Тело, которое необходимо отправить в запросе.
                {
                    "contenttype_": "text",
                    "name": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовый продукт №1"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test product №1"
                        }
                    ],
                    "price": {
                        "price": 725,
                        "currency": "RUB"
                    },
                    "comission_partner": 15,
                    "categories": [
                        {
                            "owner": 0,
                            "category_id": 7074
                        },
                        {
                            "owner": 1,
                            "category_id": 18162
                        }
                    ],
                    "bonus": {
                        "enabled": false,
                        "percent": 5
                    },
                    "guarantee": {
                        "enabled": true,
                        "value": 5
                    },
                    "description": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовое описание"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test description"
                        }
                    ],
                    "add_info": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовая дополнительная информация"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test additional information"
                        }
                    ],
                    "address_required": false,
                    "trial_url": "http://localhost",
                    "instruction": {
                        "type": "text",
                        "locales": [
                            {
                                "locale": "ru-RU",
                                "value": "Русская инструкция"
                            },
                            {
                                "locale": "en-US",
                                "value": "English instruction"
                            }
                        ]
                    },
                    "present_product_id": 123321
                }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#createsoftware"
        """
        return self.__request('POST', f'product/create/software', params={"token": self.token}, json=data)

    def product_create_arbitrary(self, data: dict):
        """
        Создание товара типа 'Произвольный цифровой товар'.

        Args:
            data (dict): Тело, которое необходимо отправить в запросе.
                {
                    "contenttype_": "text",
                    "name": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовый продукт №1"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test product №1"
                        }
                    ],
                    "price": {
                        "price": 725,
                        "currency": "RUB"
                    },
                    "affiliate_program": 0,
                    "comission_partner": 15,
                    "categories": [
                        {
                            "owner": 0,
                            "category_id": 7074
                        },
                        {
                            "owner": 1,
                            "category_id": 18162
                        }
                    ],
                    "bonus": {
                        "enabled": false,
                        "percent": 5
                    },
                    "guarantee": {
                        "enabled": true,
                        "value": 5
                    },
                    "description": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовое описание"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test description"
                        }
                    ],
                    "add_info": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовая дополнительная информация"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test additional information"
                        }
                    ],
                    "address_required": false,
                    "pay_as_you_want": true,
                    "instruction": {
                        "type": "text",
                        "locales": [
                            {
                                "locale": "ru-RU",
                                "value": "Русская инструкция"
                            },
                            {
                                "locale": "en-US",
                                "value": "English instruction"
                            }
                        ]
                    },
                    "present_product_id": 123321
                }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#createarbitrary"
        """
        return self.__request('POST', f'product/create/arbitrary', params={"token": self.token}, json=data)

    def product_edit_uniquefixed(self, product_id: int, data: dict):
        """
        Редактирование товара типа 'Уникальный товар с фиксированной ценой'.

        Args:
            product_id (int): идентификатор товара.
            data (dict): Тело, которое необходимо отправить в запросе.
                {
                    "enabled": true,
                    "name": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовый продукт №1"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test product №1"
                        }
                    ],
                    "price": {
                        "price": 725,
                        "currency": "RUB"
                    },
                    "comission_partner": 15,
                    "categories": [
                        {
                            "owner": 0,
                            "category_id": 7074
                        },
                        {
                            "owner": 1,
                            "category_id": 18162
                        }
                    ],
                    "bonus": {
                        "enabled": false,
                        "percent": 5
                    },
                    "guarantee": {
                        "enabled": true,
                        "value": 5
                    },
                    "description": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовое описание"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test description"
                        }
                    ],
                    "add_info": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовая дополнительная информация"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test additional information"
                        }
                    ],
                    "address_required": false,
                    "verify_code": {
                        "auto_verify": true,
                        "verify_url": "https://example.com/verify"
                    },
                    "preorder": {
                        "enabled": true,
                        "delivery_date": "2018-10-10"
                    }
                    "instruction": {
                        "type": "text",
                        "locales": [
                            {
                                "locale": "ru-RU",
                                "value": "Русская инструкция"
                            },
                            {
                                "locale": "en-US",
                                "value": "English instruction"
                            }
                        ]
                    },
                    "present_product_id": 123321
                }


        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#edituniquefixed"
        """
        return self.__request('POST', f'product/edit/uniquefixed/{product_id}', params={"token": self.token}, json=data)

    def product_edit_uniqueunfixed(self, product_id: int, data: dict):
        """
        Редактирование товара типа 'Уникальный товар с нефиксированной ценой'.

        Args:
            product_id (int): идентификатор товара.
            data (dict): Тело, которое необходимо отправить в запросе.
                {
                    "enabled": true,
                    "name": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовый продукт №1"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test product №1"
                        }
                    ],
                    "prices": {
                        "price": 250,
                        "unit_quantity": 1000000,
                        "currency": "RUB,
                        "unit_name": "Gold"
                    },
                    "comission_partner": 15,
                    "categories": [
                        {
                            "owner": 0,
                            "category_id": 7074
                        },
                        {
                            "owner": 1,
                            "category_id": 18162
                        }
                    ],
                    "bonus": {
                        "enabled": false,
                        "percent": 5
                    },
                    "guarantee": {
                        "enabled": true,
                        "value": 5
                    },
                    "description": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовое описание"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test description"
                        }
                    ],
                    "add_info": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовая дополнительная информация"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test additional information"
                        }
                    ],
                    "address_required": false,
                    "verify_code": {
                        "auto_verify": true,
                        "verify_url": "https://example.com/verify"
                    },
                    "discounts": [
                        {
                            "unit_for_discount": 1.0,
                            "discount": 1
                        },
                        {
                            "unit_for_discount": 1.0,
                            "discount": 1
                        }
                    ],
                    "limitations": {
                        "type": "sample string 1",
                        "only_integer": true,
                        "limitations": [
                          1,
                          2
                        ]
                    },
                    "instruction": {
                        "type": "text",
                        "locales": [
                            {
                                "locale": "ru-RU",
                                "value": "Русская инструкция"
                            },
                            {
                                "locale": "en-US",
                                "value": "English instruction"
                            }
                        ]
                    },
                    "present_product_id": 123321
                }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#edituniqueunfixed"
        """
        return self.__request('POST',
                              f'https://api.digiseller.ru/api/product/edit/uniqueunfixed/{product_id}', params={"token": self.token},
                              json=data)

    def product_edit_book(self, product_id: int, data: dict):
        """
        Редактирование товара типа 'Электронная книга'.

        Args:
            product_id (int): идентификатор товара.
            data (dict): Тело, которое необходимо отправить в запросе.
                {
                    "enabled": true,
                    "name": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовый продукт №1"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test product №1"
                        }
                    ],
                    "price": {
                        "price": 725,
                        "currency": "RUB"
                    },
                    "comission_partner": 15,
                    "categories": [
                        {
                            "owner": 0,
                            "category_id": 7074
                        },
                        {
                            "owner": 1,
                            "category_id": 18162
                        }
                    ],
                    "bonus": {
                        "enabled": false,
                        "percent": 5
                    },
                    "guarantee": {
                        "enabled": true,
                        "value": 5
                    },
                    "description": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовое описание"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test description"
                        }
                    ],
                    "add_info": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовая дополнительная информация"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test additional information"
                        }
                    ],
                    "address_required": false,
                    "trial_url": "http://localhost",
                    "instruction": {
                        "type": "text",
                        "locales": [
                            {
                                "locale": "ru-RU",
                                "value": "Русская инструкция"
                            },
                            {
                                "locale": "en-US",
                                "value": "English instruction"
                            }
                        ]
                    },
                    "present_product_id": 123321
                }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#editbook"
        """
        return self.__request('POST', f'product/edit/book/{product_id}', params={"token": self.token}, json=data)

    def product_edit_software(self, product_id: int, data: dict):
        """
        Редактирование товара типа 'Программное обеспечение'.

        Args:
            product_id (int): идентификатор товара.
            data (dict): Тело, которое необходимо отправить в запросе.
                {
                    "enabled": true,
                    "name": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовый продукт №1"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test product №1"
                        }
                    ],
                    "price": {
                        "price": 725,
                        "currency": "RUB"
                    },
                    "comission_partner": 15,
                    "categories": [
                        {
                            "owner": 0,
                            "category_id": 7074
                        },
                        {
                            "owner": 1,
                            "category_id": 18162
                        }
                    ],
                    "bonus": {
                        "enabled": false,
                        "percent": 5
                    },
                    "guarantee": {
                        "enabled": true,
                        "value": 5
                    },
                    "description": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовое описание"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test description"
                        }
                    ],
                    "add_info": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовая дополнительная информация"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test additional information"
                        }
                    ],
                    "address_required": false,
                    "trial_url": "http://localhost",
                    "instruction": {
                        "type": "text",
                        "locales": [
                            {
                                "locale": "ru-RU",
                                "value": "Русская инструкция"
                            },
                            {
                                "locale": "en-US",
                                "value": "English instruction"
                            }
                        ]
                    },
                    "present_product_id": 123321
                }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#editsoftware"
        """
        return self.__request('POST', f'product/edit/software/{product_id}', params={"token": self.token}, json=data)

    def product_edit_arbitrary(self, product_id: int, data: dict):
        """
        Редактирование товара типа 'Произвольный цифровой товар'.

        Args:
            product_id (int): идентификатор товара.
            data (dict): Тело, которое необходимо отправить в запросе.
                {
                    "enabled": true,
                    "name": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовый продукт №1"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test product №1"
                        }
                    ],
                    "price": {
                        "price": 725,
                        "currency": "RUB"
                    },
                    "comission_partner": 15,
                    "categories": [
                        {
                            "owner": 0,
                            "category_id": 7074
                        },
                        {
                            "owner": 1,
                            "category_id": 18162
                        }
                    ],
                    "bonus": {
                        "enabled": false,
                        "percent": 5
                    },
                    "guarantee": {
                        "enabled": true,
                        "value": 5
                    },
                    "description": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовое описание"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test description"
                        }
                    ],
                    "add_info": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовая дополнительная информация"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test additional information"
                        }
                    ],
                    "address_required": false,
                    "instruction": {
                        "type": "text",
                        "locales": [
                            {
                                "locale": "ru-RU",
                                "value": "Русская инструкция"
                            },
                            {
                                "locale": "en-US",
                                "value": "English instruction"
                            }
                        ]
                    },
                    "present_product_id": 123321
                }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#editarbitrary"
        """
        return self.__request('POST', f'product/edit/arbitrary/{product_id}', params={"token": self.token}, json=data)

    def product_edit_base(self, product_id: int, data: dict):
        """
        Редактирование базовых свойств товара. Включение/выключение товара.

        Args:
            product_id (int): идентификатор товара.
            data (dict): Тело, которое необходимо отправить в запросе.
               {
                    "enabled": true,
                    "name": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовый продукт №1"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test product №1"
                        }
                    ],
                    "price": {
                        "price": 725,
                        "currency": "RUB"
                    },
                    "comission_partner": 15,
                    "categories": [
                        {
                            "owner": 0,
                            "category_id": 7074
                        },
                        {
                            "owner": 1,
                            "category_id": 18162
                        }
                    ],
                    "bonus": {
                        "enabled": false,
                        "percent": 5
                    },
                    "guarantee": {
                        "enabled": true,
                        "value": 5
                    },
                    "description": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовое описание"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test description"
                        }
                    ],
                    "add_info": [
                        {
                            "locale": "ru-RU",
                            "value": "Тестовая дополнительная информация"
                        },
                        {
                            "locale": "en-US",
                            "value": "Test additional information"
                        }
                    ],
                    "address_required": false,
                    "instruction": {
                        "type": "text",
                        "locales": [
                            {
                                "locale": "ru-RU",
                                "value": "Русская инструкция"
                            },
                            {
                                "locale": "en-US",
                                "value": "English instruction"
                            }
                        ]
                    },
                    "present_product_id": 123321
                }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#editbase"
        """
        return self.__request('POST', f'product/edit/base/{product_id}', params={"token": self.token}, json=data)

    def product_preview_add_images(self, product_id: int, files):
        """
        Добавление изображений товара.

        Args:
            product_id (int): ID товара.
            files: Файлы изображений загрузить в запросе.
                Example: files = {'image.jpeg': open('pic.jpeg', 'rb')}

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#add_image_preview"
        """
        return self.__request('POST', f'product/preview/add/images/{product_id}', params={"token": self.token}, files=files)

    def product_preview_add_videos(self, product_id: int, urls: list):
        """
        Добавление youtube-ссылок в галерею.

        Args:
            product_id (int): ID товара.
            urls (list): Список с ссылками на видео ["youtube.com/...", "youtube.com/..."].

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#add_video_preview"
        """
        data = {
            "urls": urls
        }
        return self.__request('POST', f'product/preview/add/videos/{product_id}', params={"token": self.token}, json=data)

    def product_preview_options(self, type_: str, preview_id: int, enabled: bool, index: int, delete: bool):
        """
        Изменение позиции и удаление изображений в галерее.

        Args:
            type_ (str): Тип превью. Возможные значения: image или video.
            preview_id (int): ID превью.
            enabled (bool, optional): Разрешает/запрещает отображение превью на странице товара	true | false.
            index (int, optional): Устанавливает порядковый номер превью при отображении.
            delete (bool, optional): Удаляет превью из галереи	true | false.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#preview_options"
        """
        data = {
            "enabled": enabled,
            "index": index,
            "delete": delete
        }
        return self.__request('POST', f'product/preview/options/{type_}/{preview_id}', params={"token": self.token}, json=data)

    def product_edit_v2(self, new_status: str, products: list):
        """
        Массовое обновление статуса товаров.

        Args:
            new_status (str): Новый статус товара. Доступные значения: "disabled", "enabled".
            products (list): ID товаров. Не более 200 товаров в 1 запросе: ["123", "345"].

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#change_status"
        """
        data = {
            "new_status": new_status,
            "products": products
        }
        return self.__request('POST', f'product/edit/V2/status', params={"token": self.token}, json=data)

    def product_platform_category_add(self, product_id: int, category_id: int):
        """
        Добавление товара в подкатегорию торговой площадки.

        Args:
            product_id (int): ID товара.
            category_id (int): ID подкатегории торговой площадки.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#producttomarketplacesubcategory"
        """
        return self.__request('GET', f'product/platform/category/add/{product_id}/{category_id}', params={"token": self.token})

    def dictionary_platforms_categories(self, id_: str):
        """
        Получение дерева категорий торговой площадки.

        Args:
            id_ (str): Код торговой площадки. Доступные значения: 'plati', 'ggsel', 'wmcentre'.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#marketplacecategories"
        """
        return self.__request('GET', f'dictionary/platforms/categories/{id_}')

    def dictionary_platforms_subcategories(self, id_: int):
        """
        Получение подкатегорий торговой площадки.
        ВНИМАНИЕ! Данный метод актуален только для торговой площадки 'Plati.Market'.

        Args:
            id_ (int): ID категории торговой площадки.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#marketplacesubcategories"
        """
        return self.__request('GET', f'api/dictionary/platforms/subcategories/{id_}')

    def product_edit_prices(self, data: dict):
        """
        Массовое изменение цен товаров.

        Args:
            data (dict): Тело, которое необходимо отправить в запросе.
                [
                    {
                        "ProductId": 1234567,
                        "Price": 1.25
                    },
                    {
                        "ProductId": 7654321,
                        "Price": 2.25
                    },
                    ...
                ]

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#massPriceUpdate"
        """
        return self.__request('POST', f'product/edit/prices', params={"token": self.token}, json=data)

    def product_edit_update_products_tasks_status(self, task_id: str):
        """
        Получение статуса выполнения асинхронной задачи.

        Args:
            task_id (str): ID для отслеживания выполнения задачи.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_goods.asp#productsUpdateStatus"
        """
        params = {
            "taskId": task_id,
            "token": self.token
        }
        return self.__request('GET', f'product/edit/UpdateProductsTaskStatus', params=params)

    """ Добавление содержимого товаров """

    def product_content_add_file(self, product_id: int, file):
        """
        Метод добавления содержимого типа 'Файл'.

        Args:
            product_id (int): идентификатор товара.
            file: Файл загрузить в запросе.
                Example: files = {'text.txt': open('passwords.txt', 'rb')}

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_content.asp#addfile"
        """
        return self.__request('POST', f'product/content/add/file/{product_id}', params={"token": self.token}, files=file)

    def product_content_add_files(self, product_id: int, count: int, files):
        """
        Метод добавления содержимого типа "Файл" с распаковкой ZIP-архива (до 200 файлов).
        Внимание! Файлы в ZIP-архиве не должны находиться во внутренних папках. Такие файлы будут игнорированы.

        Args:
            product_id (int): ID товара.
            count (int): Количество файлов ZIP архиве.
            files: Файлы, необходимо загрузить в запросе.
                Example: files = {'archive1': ('filename.zip', open('path/to/your/file1.zip', 'rb'))}

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_content.asp#addfiles"
        """
        return self.__request('POST', f'product/content/add/files/{product_id}/{count}', params={"token": self.token}, files=files)

    def product_content_add_text(self, data: dict):
        """
        Добавление содержимого типа 'текст' или 'ссылка'.

        Args:
            data: Тело, которое необходимо отправить в запросе.
                {
                    "product_id": 222,
                    "content":
                    [
                        {
                            "serial": "test",
                            "value": "Test value",
                            "id_v": 0
                        },
                        {
                            "value": "Test value #2",
                            "id_v": 0
                        }
                    ]
                }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_content.asp#addtext"
        """

        return self.__request('POST', f'product/content/add/text', params={"token": self.token}, json=data)

    def product_content_add_code(self, product_id: int, count: int):
        """
        Изменение количества генерируемых кодов Digiseller.

        Args:
            product_id (int): ID товара.
            count (int): Количество генерируемых кодов.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_content.asp#addcode"
        """
        return self.__request('GET', f'product/content/add/code/{product_id}/{count}', params={"token": self.token})

    def product_content_update_file_v2(self, files: dict, content_id: int, product_id: int, update_old: bool):
        """
        Метод редактирования содержимого типа 'Файл'.

        Args:
            content_id (int): ID содержимого.
            product_id (int): ID товара.
            update_old (bool): Обновить проданное содержимое (только для универсальных файлов).	По умолчанию: false.
            files (dict): Файлы, необходимо отправить в запросе.
                Example:
                    files = {
                    '1': ('image1.jpeg', open('1.jpeg', 'rb')),
                    '2': ('image2.jpeg', open('2.jpeg', 'rb'))
                    }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_content.asp#updateFile"
        """
        if product_id is None:
            params = {
                "contentid": content_id,
                "updateold": update_old,
                "token": self.token
            }
            return self.__request('POST', f'product/content/update/file/v2', files=files, headers={'Content-Type': 'multipart/form-data'}, params=params)
        params = {
            ""
            "contentid": product_id,
            "updateold": update_old,
            "token": self.token
        }
        return self.__request('POST', f'product/content/update/file/v2', files=files, headers={'Content-Type': 'multipart/form-data'}, params=params)

    def product_content_update_text(self, content_id: int, serial: str, value: str, update_old: bool,
                                    product_id: int):
        """
        Редактирование содержимого типа 'текст' или 'ссылка'.

        Args:
            content_id (int): ID содержимого.
            product_id (int): ID товара.
            serial (str, optional): Ваш код отслеживания. Необязательное поле.
            value (str): Содержимого товара. Обязательное поле.
            update_old (bool): Обновить проданное содержимое (только для универсальных товаров). По умолчанию: false.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_content.asp#updateText"
        """
        if content_id:
            data = {
                "value": value,
                "serial": serial,
                "update_old": update_old,
                "content_id": content_id
            }
        else:
            data = {
                "value": value,
                "serial": serial,
                "update_old": update_old,
                "product_id": product_id
            }
        return self.__request('POST', f'product/content/update/text', params={"token": self.token}, json=data)

    def product_content_delete(self, content_id: int, product_id: int):
        """
        Удаление содержимого типа 'текст', 'ссылка' или 'файл'.

        Args:
            content_id (int): ID содержимого.
            product_id (int): ID товара.

        Returns:
            Response: 'StatusCode: 204 (NoContent)'
            URL INFO: "https://my.digiseller.com/inside/api_content.asp#deleteContent"
        """
        params = {
            "contentid": content_id,
            "productid": product_id,
            "token": self.token
        }

        return self.__request('GET', f'product/content/delete', params=params)

    def product_content_delete_all(self, product_id: int):
        """
        Полное удаление содержимого типа 'текст', 'ссылка' или 'файл'.

        Args:
            product_id (int): ID товара.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_content.asp#deleteAllContent"
        """
        params = {
            "productid": product_id,
            "token": self.token
        }
        return self.__request('GET', f'product/content/delete/all', params=params)

    def product_content_update_form(self, product_id: int, address: str, method: str, encoding: str, options: bool,
                                    answer: bool, allow_purchase_multiple_items: bool, url_for_quantity: str):
        """
        Создание или редактирование содержимого типа 'форма'.

        Args:
            product_id (int): ID товара.
            address (str): Email Адрес
            method (str): Способ отправки. Доступные значения: Email, JSON, XML.
            encoding (str): Кодировка.
            options (bool): Отправлять параметры - True/False.
            answer (bool): Ответ от сервера содержит товар - True/False.
            allow_purchase_multiple_items (bool): Разрешать покупку нескольких единиц - True/False.
            url_for_quantity (str, optional): Url для отправки запроса с количеством, которое указал покупатель.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_content.asp#update_form"
        """
        data = {
            "product_id": 1,
            "address": address,
            "method": method,
            "encoding": encoding,
            "options": options,
            "answer": answer,
            "allow_purchase_multiple_items": allow_purchase_multiple_items,
            "url_for_quantity": url_for_quantity
        }
        params = {
            "productid": product_id,
            "token": self.token
        }
        return self.__request('POST', f'product/content/delete/all', json=data, params=params)

    """ Шаблоны отчислений """

    def templates(self, name: str):
        """
        Cоздание шаблона комиссионных отчислений.

        Args:
            name (str): Наименование шаблона. Название шаблона комиссии.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_templates.asp#create_template"
        """
        return self.__request('POST', f'templates', params={"token": self.token}, json={"name": name})

    def templates_edit(self, name: str, id_: int):
        """
        Изменение шаблона комиссионных отчислений.

        Args:
            name (str): Наименование шаблона. Название шаблона комиссии.
            id_ (int): ID шаблона

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_templates.asp#edit_template"
        """
        data = {"name": name}
        return self.__request('POST', f'templates/{id_}', params={"token": self.token}, json=data)

    def templates_list(self, page: int, count: int):
        """
        Получение списка шаблонов отчислений.

        Args:
            page (int): Номер страницы.
            count (int): Количество на странице, от 1 до 100.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_templates.asp#get_list_templates"
        """
        params = {
            "page": page,
            "count": count,
            "token": self.token
        }
        return self.__request('GET', f'templates', params=params)

    def templates_delete(self, id_: int, method: str = "POST"):
        """
        Удаление шаблона комиссионных отчислений.

        Args:
            method (str, optional): Метод отправки запроса - POST or DELETE.
            id_ (int): ID шаблона

        Returns:
            StatusCode: 204 (NoContent)
            URL INFO: "https://my.digiseller.com/inside/api_templates.asp#delete_template"
        """
        if method == "POST":
            return self.__request('POST', f'templates/delete/{id_}', params={"token": self.token})
        return self.__request('DELETE', f'templates/{id_}', params={"token": self.token})

    def templates_products(self, template_id: int, product_id: int, price_min: float,
                           price_max: float,
                           currency: str, language: str, name: str, min_comiss: float,
                           max_comiss: float, in_affiliate: bool, not_in_affiliate: bool,
                           only_payment: bool, page: int, count: int):
        """
        Получение списка товаров из шаблона отчислений.

        Args:
            template_id (int): ID шаблона.
            product_id (int, optional): ID товара.
            price_min (float, optional): Минимальная цена.
            price_max (float, optional): Максимальная цена.
            currency (str, optional): Валюта (RUB|USD|UAH|EUR).
            language (str, optional): Язык отображения информации ('ru-RU', 'en-US').
            name (str, optional): Строка поиска.
            min_comiss (float, optional): Минимальная комиссия.
            max_comiss (float, optional): Максимальная комиссия.
            in_affiliate (bool, optional): Отображать товары, участвующие в партнерской программе (True|False).
            not_in_affiliate (bool, optional): Отображать товары, не участвующие в партнерской программе (True|False).
            only_payment (bool, optional): Только доступные для оплаты товары (True|False).
            page (int, optional): Номер страницы.
            count (int, optional): Количество на странице (до 100).

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_templates.asp#get_products"
        """
        params = {
            "templateId": template_id,
            "productId": product_id,
            "priceMin": price_min,
            "priceMax": price_max,
            "currency": currency,
            "language": language,
            "name": name,
            "minComiss": min_comiss,
            "maxComiss": max_comiss,
            "inAffiliate": in_affiliate,
            "notInAffiliate": not_in_affiliate,
            "onlyPayment": only_payment,
            "page": page,
            "count": count,
            "token": self.token
        }

        return self.__request('GET', f'templates/products', params=params)

    def update_template_products(self, data: dict):
        """
        Обновление товаров в шаблоне отчислений.

        Args:
            data (dict): Тело запроса.
                {
                    "template_id": 1,
                    "products": [
                        {
                            "product_id": 1,
                            "percent": 2
                        },
                        {
                            "product_id": 2,
                            "percent": 5
                        }
                    ]
                }

        Returns:
            Response: 'StatusCode: 204 (NoContent)'
            URL INFO: "https://my.digiseller.com/inside/api_templates.asp#edit_products"
        """
        return self.__request('POST', f'templates/products', params={"token": self.token}, json=data)

    def template_apply(self, template_id: int, seller_id: int):
        """
        Применение шаблона отчислений.

        Args:
            template_id (int): ID шаблона.
            seller_id (dict): Список товаров и их процентов.

        Returns:
            Response: 'StatusCode: 204 (NoContent)'
            URL INFO: "https://my.digiseller.com/inside/api_templates.asp#apply"
        """
        data = {
            "template_id": template_id,
            "seller_id": seller_id
        }

        return self.__request('POST', f'templates/apply', params={"token": self.token}, json=data)

    """ Параметры товара """

    def products_options_list(self, product_id: int):
        """
        Список параметров товара.

        Args:
            product_id (int): ID товара.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_parameters.asp#getlist"
        """

        return self.__request('GET', f'products/options/list/{product_id}', params={"token": self.token})

    def products_options_info(self, option_id: int):
        """
        Информация о параметре.

        Args:
            option_id (int): ID параметра.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_parameters.asp#getfull"
        """

        return self.__request('GET', f'products/options/{option_id}', params={"token": self.token})

    def products_options_add(self, name_ru: str, name_en: str, comment_ru: str, comment_en: str, ptype: str,
                             separate_content: bool, required: bool, modifier_visible: bool, order: int,
                             product_id: int, variant_dict: dict):
        """
        Создание параметра.

        Args:
            name_ru (str): Наименование параметра на русском языке.
            name_en (str): Наименование параметра на английском языке
            comment_ru (str): Комментарий к параметру на русском языке.
            comment_en (str): Комментарий к параметру на английском языке.
            ptype (str): Тип параметра. Доступные значения:'textarea', 'checkbox', 'text', 'radio', 'select'.
            separate_content (bool): Признак наличия раздельного содержимого по варианту параметра товара.
            required (bool): Параметр является обязательным.
            modifier_visible (bool): Скрыть модификатор цены.
            order (int): Номер сортировки (начинается с 1).
            product_id (int): ID товара.
            variant_dict (dict): При необходимости добавления варианта (подпараметры), передать их:
                Example: [
                    {
                      "name": [
                        {
                          "locale": "ru-RU",
                          "value": "тестовый вариант"
                        },
                        {
                          "locale": "en-US",
                          "value": "test variant"
                        }
                      ],
                      "type": "priceplus",
                      "rate": 1,
                      "default": true,
                      "order": 1
                    },
                    {
                      "name": [
                        {
                          "locale": "ru-RU",
                          "value": "тестовый вариант 2"
                        },
                        {
                          "locale": "en-US",
                          "value": "test variant 2"
                        }
                      ],
                      "type": "percentminus",
                      "rate": 1,
                      "default": false,
                      "order": 2
                    }
                  ]

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_parameters.asp#createparam"
        """
        comment = None
        variants = None
        if comment_ru is not None:
            comment = [{"locale": "ru-RU", "value": comment_ru}, {"locale": "en-US", "value": comment_en}]
        if variant_dict is not None:
            variants = variant_dict

        data = {
            "name": [{"locale": "ru-RU", "value": name_ru}, {"locale": "en-US", "value": name_en}],
            "comment": comment,
            "type": ptype,
            "separate_content": separate_content,
            "required": required,
            "modifier_visible": modifier_visible,
            "order": order,
            "product_id": product_id,
            "variants": variants
        }

        return self.__request('POST', f'products/options', params={"token": self.token}, json=data)

    def products_options_update(self, name_ru: str, name_en: str, ptype: str,
                                separate_content: bool, required: bool, modifier_visible: bool, order: int,
                                option_id: int, comment_ru: str, comment_en: str):
        """
        Редактирование параметра.

        Args:
            name_ru (str): Наименование параметра на русском языке.
            name_en (str): Наименование параметра на английском языке
            comment_ru (str, optional): Комментарий к параметру на русском языке.
            comment_en (str, optional): Комментарий к параметру на английском языке.
            ptype (str): Тип параметра. Доступные значения:'textarea', 'checkbox', 'text', 'radio', 'select'.
            separate_content (bool): Признак наличия раздельного содержимого по варианту параметра товара.
            required (bool): Параметр является обязательным.
            modifier_visible (bool): Скрыть модификатор цены.
            order (int): Номер сортировки (начинается с 1).
            option_id (int, optional): ID параметра.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_parameters.asp#editparam"
        """
        comment = None
        if comment_ru is not None:
            comment = [{"locale": "ru-RU", "value": comment_ru}, {"locale": "en-US", "value": comment_en}]

        data = {
            "name": [{"locale": "ru-RU", "value": name_ru}, {"locale": "en-US", "value": name_en}],
            "comment": comment,
            "type": ptype,
            "separate_content": separate_content,
            "required": required,
            "modifier_visible": modifier_visible,
            "order": order,
            "option_id": option_id
        }

        return self.__request('POST', f'products/options/update', params={"token": self.token}, json=data)

    def products_options_delete(self, option_id: int):
        """
        Удаление параметра.

        Args:
            option_id (int, optional): ID параметра.


        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_parameters.asp#deleteparam"
        """

        return self.__request('GET', f'products/options/{option_id}/delete', params={"token": self.token})

    def products_variant_add(self, option_id: int, data: dict):
        """
        Создание варианта.

        Args:
            option_id (int): ID параметра.
            data (dict): Тело запроса.
                {
                  "variants": [
                    {
                      "name": [
                        {
                          "locale": "ru-RU",
                          "value": "тестовый вариант"
                        },
                        {
                          "locale": "en-US",
                          "value": "test variant"
                        }
                      ],
                      "type": "priceplus",
                      "rate": 1,
                      "default": true,
                      "order": 1
                    },
                    {
                      "name": [
                        {
                          "locale": "ru-RU",
                          "value": "тестовый вариант 2"
                        },
                        {
                          "locale": "en-US",
                          "value": "test variant 2"
                        }
                      ],
                      "type": "percentminus",
                      "rate": 1,
                      "default": false,
                      "order": 2
                    }
                  ]
                }

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_parameters.asp#createvariant"
        """

        return self.__request('POST', f'products/options/{option_id}/variants', params={"token": self.token}, json=data)

    def products_variant_edit(self, option_id: int, variant_id: int, name_ru: str, name_en: str, ptype: str, rate: int, default: bool, visible: bool, order: int):
        """
        Редактирование варианта.

        Args:
            option_id (int): ID параметра.
            variant_id (int): ID варианта.
            name_ru (str): Наименование варианта на русском языке.
            name_en (str): Наименование варианта на английском языке
            ptype (str): Модификатор цены. Доступные значения: 'percentplus', 'percentminus', 'priceplus', 'priceminus'.
            rate (str): Значение модификатора. Дробное число.
            default (str): 	По умолчанию.
            visible (bool): Скрыто.
            order (bool): Номер сортировки (начинается с 1).


        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_parameters.asp#editvariant"
        """

        data = {
            "name": [{"locale": "ru-RU", "value": name_ru}, {"locale": "en-US", "value": name_en}],
            "type": ptype,
            "rate": rate,
            "default": default,
            "visible": visible,
            "order": order
        }

        return self.__request('POST', f'products/options/{option_id}/variants/{variant_id}', params={"token": self.token}, json=data)

    def products_variant_delete(self, option_id: int, variant_id: int):
        """
        Удаление варианта.

        Args:
            option_id (int): ID параметра.
            variant_id (int): ID варианта.


        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_parameters.asp#deletevariant"
        """

        return self.__request('GET', f'products/options/{option_id}/variants/{variant_id}/delete', params={"token": self.token})

    """ Переписка с покупателями """

    def chat_list(self, filter_new: int, pagesize: int, page: int, email=None, id_ds=None):
        """
        Получение списка диалогов.

        Args:
            filter_new (int, optional): Фильтр непрочитанных сообщений.
            email (str, optional): Фильтр по email'у покупателя.
            id_ds (str, optional): Фильтр по id товаров.
            pagesize (int,optional): Диалогов на странице (до 200).
            page (int, optional): Номер страницы.


        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_debates.asp#get_chats"
        """

        params = {
            "token": self.token,
            'filter_new': filter_new,
            'email': email,
            'id_ds': id_ds,
            'pagesize': pagesize,
            'page': page
        }

        return self.__request('GET', f'debates/v2/chats', params=params)

    def chat_status(self, id_i: int):
        """
        Получение статуса диалога.

        Args:
            id_i (int): Номер заказа.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_debates.asp#get_state"
        """
        params = {
            "token": self.token,
            "id_i": id_i
        }
        return self.__request('GET', f'debates/v2/chat-state', params=params)

    def chat_edit_status(self, id_i: int, chat_state: int):
        """
        Изменение статуса диалога.

        Закрытие диалога невозможно если он был открыт администрацией.
        Возможно закрыть диалог после возврата денежных средств.

        Args:
            id_i (int): Фильтр непрочитанных сообщений.
            chat_state (int): Фильтр по Email'у покупателя.


        Returns:
            Response: 'StatusCode: 200 (NoContent)'
            URL INFO: "https://my.digiseller.com/inside/api_debates.asp#post_state"
        """
        params = {
            "token": self.token,
            "id_i": id_i,
            "chat_state": chat_state
        }
        return self.__request('POST', f'debates/v2/chat-state', params=params)

    def chat_order_messages(self, id_i: int, hidden: int, id_from: int, id_to: int, old_id: int, newer: int, count: int):
        """
        Получение списка сообщений.

        Args:
            id_i (int): Номер заказа.
            hidden (int): Возвращать удаленные сообщения (0|1).
            id_from (int): ID сообщения начиная с которого нужно получить.
            id_to (int): ID сообщения до которого нужно получить (включительно).
            old_id (int): ID сообщения который уже был получен. Игнорируется, если заданы id_from и id_to.
            newer (int): Возвращать все не полученные сообщения (0|1).
            count (int): Сколько сообщений нужно возвращать (до 200). Игнорируется, если заданы id_from и id_to, или newer.


        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_debates.asp#get_debates"
        """

        params = {
            "token": self.token,
            "id_i": id_i,
            'hidden': hidden,
            'id_from': id_from,
            'id_to': id_to,
            'old_id': old_id,
            'newer': newer,
            'count': count
        }

        return self.__request('GET', f'debates/v2', params=params)

    def chat_set_flag(self, id_i: int):
        """
        Установка флага прочитан.

        Args:
            id_i (int): Номер заказа.

        Returns:
            Response: 'StatusCode: 200 (NoContent)'
            URL INFO: "https://my.digiseller.com/inside/api_debates.asp#post_seen"
        """
        params = {
            "token": self.token,
            "id_i": id_i
        }
        return self.__request('POST', f'debates/v2/seen', params=params)

    def chat_upload_preview(self, files, lang: str):
        """
        Предварительная загрузка файлов.

        Args:
            lang (str): Язык отображения информации	ru-RU (по умолчанию) или en-US.
            files: Файлы для отправки в бинарном виде. "files[]": binary data.
                Example: [('files[]', ('file': open(file_path, 'rb'))]

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_debates.asp#upload_preview"
        """
        params = {
            "token": self.token,
            "lang": lang
        }
        return self.__request('POST', f'debates/v2/upload-preview', params=params, headers={'Content-Type': 'multipart/form-data'}, files=files)

    def chat_send_message(self, id_i: int, data: dict):
        """
        Отправка нового сообщения.

        Args:
            id_i (int): Номер заказа.
            data (dict): Тело, которое необходимо отправить в запросе.
                {
                  "message": "",
                  "files": [
                    {
                      "newid": "",
                      "name": "",
                      "type": ""
                    },
                    ...
                  ]
                }

        Returns:
            Response: 'StatusCode: 200 (NoContent)'
            URL INFO: "https://my.digiseller.com/inside/api_debates.asp#post_debate"
        """
        params = {
            "token": self.token,
            "id_i": id_i
        }
        headers = {'Accept': 'application/json; charset=UTF-8'}
        if 'files' in data:
            headers = {'Content-Type': 'multipart/form-data'}
        return self.__request('POST', f'debates/v2/', params=params, json=data, headers=headers)

    def chat_delete_message(self, order_id: int, message_id: int):
        """
        Удаление сообщения.

        Args:
            order_id (int): Номер заказа.
            message_id (int): ID сообщения.

        Returns:
            Response: '[] (NoContent)'
            URL INFO: "https://my.digiseller.com/inside/api_debates.asp#delete_debate"
        """
        params = {
            "token": self.token,
            "id_i": order_id
        }
        return self.__request('DELETE', f'debates/v2/{message_id}', params=params)

    """ РЕКЛАМА НА ПЛОЩАДКЕ """

    def rekl(self, owner: int, date: str, lang: str):
        """
        Реклама на площадке.

        Args:
            owner (int): ID торговой площадки.
            date (str): Дата.
            lang (str, optional): Язык отображения информации.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_rekl.asp#rekl"
        """
        params = {
            'owner': owner,
            'date': date,
            'lang': lang
        }

        return self.__request('GET', f'rekl', params=params)

    """ Операции """

    def sellers_account_receipts(self, page: int, count: int, currency: str, types: list, code_filter: str, allowtype: str, start: str, finish: str):
        """
        Получение информации об операциях по личному счету Digiseller.

        Args:
            page (int): Страница.
            count (int): Количество.
            currency (str): Валюта (WMR|WMZ|WME).
            types (list): Список типов операций.
            code_filter (str): Операции, ожидающие проверки кода ('only_waiting_check_code' или 'hide_waiting_code_check').
            allowtype (str): Операции недоступные для вывода ('exclude' или 'only').
            start (str): Начальная дата (Формат: 'yyyy-MM-dd' или 'yyyy-MM-ddTHH:mm').
            finish (str): Конечная дата (Формат: 'yyyy-MM-dd' или 'yyyy-MM-ddTHH:mm').

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_account.asp#digiseller"
        """
        params = {
            "token": self.token,
            "page": page,
            "count": count,
            "currency": currency,
            "codeFilter": code_filter,
            "allowType": allowtype,
            "start": start,
            "finish": finish
        }

        for i, type_op in enumerate(types):
            params[f"type[{i}]"] = type_op

        return self.__request('GET', f'sellers/account/receipts', params=params)

    def sellers_account_receipts_external(self, page: int, count: int, order: str, code: str, aggregator: str):
        """
        Операции через внешних агрегаторов.

        Args:
            page (int): Номер страницы.
            count (int): Количество операций на странице.
            order (str): Способ сортировки операций.
            code (str): Фильтр по операциям, ожидающим проверки кода ('only' или 'exclude').
            aggregator (str): Код агрегатора.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_account.asp#external"
        """

        params = {
            "token": self.token,
            "order": order,
            "count": count,
            "page": page,
            "code": code,
            "aggregator": aggregator
        }

        return self.__request('GET', f'sellers/account/receipts/external', params=params)

    def sellers_account_balance(self):
        """
        Информация о балансе личного счёта.

        Returns:
            dict: Ответ от сервера в формате JSON.
            URL INFO: "https://my.digiseller.com/inside/api_account.asp#view_balance"
        """

        return self.__request('GET', f'sellers/account/balance/info', params={"token": self.token})
