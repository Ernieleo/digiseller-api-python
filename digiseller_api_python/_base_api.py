import hashlib
import time
from typing import Optional

from digiseller_api_python._exceptions import DigisellerError, DigisellerInvalidResponseError
from digiseller_api_python._request_handler import send_request

class DigisellerApi:
    URL = 'https://api.digiseller.ru/api/'
    TOKEN_LIFETIME = 6600  # Token lifetime in seconds

    def __init__(self, seller_id: str, api_key: str, timeout: int = 60, proxy: str = None):
        if not isinstance(seller_id, str) or not seller_id:
            raise DigisellerError("You must pass the correct 'seller_id'.")
        if not isinstance(api_key, str) or not api_key:
            raise DigisellerError("You must pass the correct 'api_key'.")

        self.seller_id = int(seller_id)
        self.api_key = api_key
        self.timeout = timeout
        self.proxy = proxy
        self.token_expiration = 0
        self.token = None

    def _send_request(self, method, url, **kwargs):
        """Внутренний метод для отправки запросов с учетом настроек экземпляра класса."""
        return send_request(method, url, timeout=self.timeout, proxy=self.proxy, **kwargs)

    def _token_response(self):
        current_time = int(time.time())
        sign = hashlib.sha256((self.api_key + str(current_time)).encode()).hexdigest()
        data = {
            "seller_id": self.seller_id,
            "timestamp": current_time,
            "sign": sign,

        }
        response = self._send_request('POST', self.URL + 'apilogin', json=data)
        return response

    def _get_valid_token(self):
        if not self.token or int(time.time()) >= self.token_expiration:
            return self.get_token()
        return self.token

    # Получение токена для api.digiseller.ru
    # Getting the token for api.digiseller.ru
    def get_token(self):
        current_time = int(time.time())
        token_validation = self._token_response()
        if token_validation.get('retval') == 0 and token_validation.get('token'):
            self.token = token_validation['token']
            self.token_expiration = current_time + self.TOKEN_LIFETIME
            return self.token
        else:
            raise DigisellerInvalidResponseError(f"Error obtaining authorization token on the server: {token_validation.get('desc')}")

    # Получение номера запроса и капчи
    # Obtaining the request number and captcha
    def agent_get(self, seller_id):
        params = {"id_seller": seller_id}
        url = 'https://shop.digiseller.ru/xml/agent_get.asp'
        return self._send_request('GET', url, params=params, headers={'Content-Type': 'text/json'})

    # Проверка капчи и регистрация партнера
    # Captcha verification and partner registration
    def agent_check(self, seller_id, id_request: int, turing_num: int, r_email: str, r_redirect_url: str):
        params = {
            "id_seller": seller_id,
            "id_request": id_request,
            "turing_num": turing_num,
            "r_email": r_email,
            "r_redirect_url": r_redirect_url
        }
        url = 'https://shop.digiseller.ru/xml/agent_check.asp'
        return self._send_request('GET', url, params=params)

    # Список разрешений
    # Permission list
    def perms_token(self):
        params = {"token": self._get_valid_token()}
        endpoint = 'token/perms'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Поиск и проверка платежа по уникальному коду
    # Search and verification of payments by a unique code
    def unique_code(self, unique_code):
        """
        :param unique_code: Unique code received from the buyer
        """
        params = {"token": self._get_valid_token()}
        endpoint = f'purchases/unique-code/{unique_code}'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Перевод статуса уникального кода в "товар доставлен"
    # Change the status of the unique code to "goods delivered"
    def purchases_uniquecode_delivered(self, unique_code: str):
        """
        :param unique_code: Unique code received from the buyer
        """
        params = {"token": self._get_valid_token()}
        endpoint = f'purchases/unique-code/{unique_code}/deliver'
        return self._send_request('PUT', self.URL + endpoint, params=params)

    # Информация о продаже по номеру заказа
    # Sales information by order number
    def purchase_info(self, invoice_id):
        params = {"token": self._get_valid_token()}
        endpoint = f'purchase/info/{invoice_id}'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Список последних продаж
    # List of latest sales
    def seller_last_sales(self, group=True, top=1000):
        params = {
            "token": self._get_valid_token(),
            "seller_id": self.seller_id,
            "group": group,
            "top": top
        }
        endpoint = 'seller-last-sales'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Статистика продаж
    # Sales statistics
    def seller_sells_statistic(self, product_ids: list, date_start: str, date_finish: str, returned: int, page: int, rows: int):
        params = {"token": self._get_valid_token()}
        data = {
            "product_ids": product_ids,
            "date_start": date_start,
            "date_finish": date_finish,
            "returned": returned,
            "page": page,
            "rows": rows
        }
        endpoint = 'seller-sells/v2'
        return self._send_request('POST', self.URL + endpoint, params=params, json=data)

    # Статистика продаж в роли агента
    # Sales statistics as an agent
    def agent_sales_statistic(self, product_ids: list, date_start: str, date_finish: str, returned: int, page: int, rows: int):
        params = {"token": self._get_valid_token()}
        data = {
            "product_ids": product_ids,
            "date_start": date_start,
            "date_finish": date_finish,
            "returned": returned,
            "page": page,
            "rows": rows
        }
        endpoint = 'agent-sales/v2'
        return self._send_request('POST', self.URL + endpoint, params=params, json=data)

    # Список категорий (каталог)
    # The list of categories (catalog)
    def categories_list(self, category_id: int, lang: str):
        params = {
            "seller_id": self.seller_id,
            "category_id": category_id,
            "lang": lang
        }
        endpoint = f'categories'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Список товаров из категории
    # The list of products from the category
    def categories_products(self, category_id: int, page: int, rows: int, order: str, currency: str, lang: str):
        params = {
            "seller_id": self.seller_id,
            "category_id": category_id,
            "page": page,
            "rows": rows,
            "order": order,
            "currency": currency,
            "lang": lang
        }
        endpoint = f'shop/products'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Быстрое получение описаний товаров по списку ID
    # Quickly get product descriptions from ID list
    def products_list_description(self, ids: list, lang: str, use_token = True):
        data = {
            "ids": ids,
            "lang": lang,
        }
        if use_token:
            data["token"] = self._get_valid_token()
        endpoint = f'products/list'
        return self._send_request('POST', self.URL + endpoint, json=data)

    # Описание товара
    # Product description
    def products_description(self, product_id: int, seller_id: int, partner_uid: str, currency: str, lang: str, owner: int, show_hidden_variants: int):
        params = {
            "seller_id": seller_id,
            "partner_uid": partner_uid,
            "currency": currency,
            "lang": lang,
            "token": self.token,
            "owner": owner,
            "showHiddenVariants": show_hidden_variants
        }
        endpoint = f'products/{product_id}/data'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Получение цены с учетом входящих значений параметров и/или количества товара
    # Obtaining a price taking into account the input values of the parameters and/or quantity of the product
    def products_price_calc(self, product_id: int, options: list, currency: str, amount: int, unit_cnt: int, count: int):
        params = {
            "product_id": product_id,
            "options": options,
            "currency": currency,
            "amount": amount,
            "unit_cnt": unit_cnt,
            "count": count
        }
        endpoint = f'products/price/calc'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Отзывы о товарах
    # Products reviews
    def product_reviews(self, seller_id: int, product_id: int, type_: str, owner_id: int, page: int, rows: int, lang: str):
        params={
            "seller_id": seller_id,
            "product_id": product_id,
            "type": type_,
            "owner_id": owner_id,
            "page": page,
            "rows": rows,
            "lang": lang
        }
        endpoint = f'reviews'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Товары продавца
    # Items of seller
    def seller_goods(self, seller_id: int, order_col: str, order_dir: str, rows: int, page: int, currency: str, lang: str, show_hidden: int, owner_id: int):
        data = {
            "id_seller": seller_id,
            "order_col": order_col,
            "order_dir": order_dir,
            "rows": rows,
            "page": page,
            "currency": currency,
            "lang": lang,
            "show_hidden": show_hidden,
            "owner_id": owner_id,
        }
        params = {"token": self._get_valid_token()}
        endpoint = f'seller-goods'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Скидка по товару
    # Product discount
    def shop_discount(self, product_id: int, products_currency: str, email: str):
        xml_data = f"""
            <digiseller.request>
                <product>
                    <id>{product_id}</id>
                    <currency>{products_currency}</currency>
                </product>
                <email>{email}</email>
            </digiseller.request>
            """
        url = f'https://shop.digiseller.ru/xml/shop_discount.asp'
        return self._send_request('POST', url, data=xml_data)

    # Поиск по товарам
    # Product search
    def shop_search(self, seller_id: int, products_search: str, products_currency: str, pages_num: int, pages_rows: int, lang: str):
        xml_data = f"""	
            <digiseller.request>
                <seller>
                    <id>{seller_id}</id>
                </seller>
                <products>
                    <search>{products_search}</search>
                    <currency>{products_currency}</currency>
                </products>
                <pages>
                    <num>{pages_num}</num>
                    <rows>{pages_rows}</rows>
                </pages>
                <lang>{lang}</lang>
            </digiseller.request>
            """
        url = f'https://shop.digiseller.ru/xml/shop_search.asp'
        return self._send_request('POST', url, data=xml_data)

    # Быстрое получение основного изображения товара
    # Quickly get the main product image
    def get_main_img(self, id_d: int, maxlength: int, w: int, h: int, crop: bool):
        params = {
            "id_d": id_d,
            "maxlength": maxlength,
            "w": w,
            "h": h,
            "crop": crop
        }
        url = 'https://graph.digiseller.ru/img.ashx'
        return self._send_request('GET', url, params=params)

    # Создание копии описания товара (клонирование без содержимого)
    # Creation of a copy of the product description (cloning without contents)
    def product_clone(self, product_id: int, count: int, categories: bool, notify: bool, discounts: bool, options: bool, commissions: bool, gallery: bool):
        data = {
            "count": count,
            "categories": categories,
            "notify": notify,
            "discounts": discounts,
            "options": options,
            "comissions": commissions,
            "gallery": gallery
        }
        params = {"token": self._get_valid_token()}
        endpoint = f'product/clone/{product_id}'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Список товаров продавца с индивидуальным предложением
    # List of goods seller with an individual offer
    def agents_offer(self, seller_id: int, product_name: str, product_id: int, only_in_stock: bool, only_individual: bool, page: int, count: int):
        params = {
            "sellerId": seller_id,
            "productName": product_name,
            "productId": product_id,
            "onlyInStock": only_in_stock,
            "onlyIndividual": only_individual,
            "page": page,
            "count": count,
            "token": self._get_valid_token()
        }
        endpoint = f'agents/offer'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Создание товара типа "Уникальный товар с фиксированной ценой"
    # Creation of product of type "Unique product with fixed price"
    def product_create_uniquefixed(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/create/uniquefixed'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Создание товара типа "Уникальный товар с нефиксированной ценой"
    # Creation of goods of "Unique item with variable price" type
    def product_create_uniqueunfixed(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/create/uniqueunfixed'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Создание товара типа "Электронная книга"
    # Creation of goods of "Electronic books" type
    def product_create_book(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/create/book'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Создание товара типа "Программное обеспечение"
    # Creation of goods of "Software" type
    def product_create_software(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/create/software'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Создание товара типа "Произвольный цифровой товар"
    # Creation of goods of "Arbitrary digital product" type
    def product_create_arbitrary(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/create/arbitrary'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование товара типа "Уникальный товар с фиксированной ценой"
    # Editing of product of type "Unique product with fixed price"
    def product_edit_uniquefixed(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/uniquefixed/{product_id}'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование товара типа "Уникальный товар с нефиксированной ценой"
    # Editing of goods of "Unique item with variable price" type
    def product_edit_uniqueunfixed(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/uniqueunfixed/{product_id}'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование товара типа "Электронная книга"
    # Editing of goods of "Electronic books" type
    def product_edit_book(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/book/{product_id}'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование товара типа "Программное обеспечение"
    # Editing of goods of "Software" type
    def product_edit_software(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/software/{product_id}'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование товара типа "Произвольный цифровой товар"
    # Editing of goods of "Arbitrary digital product" type
    def product_edit_arbitrary(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/arbitrary/{product_id}'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование базовых свойств товара. Включение / выключение товара.
    # Editing of base props of product. Switch on/off sales.
    def product_edit_base(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/base/{product_id}'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Добавление изображений товара
    # Add product images
    def product_preview_add_images(self, product_id: int, files: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/preview/add/images/{product_id}'
        return self._send_request('POST', self.URL + endpoint, files=files, params=params)

    # Добавление youtube-ссылок в галерею
    # Adding a youtube links to the gallery
    def product_preview_add_videos(self, product_id: int, urls: list):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/preview/add/videos/{product_id}'
        data = {"urls": urls}
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Изменение позиции и удаление изображений в галерее
    # Changing the image position in gallery
    def product_preview_options(self, type_: str, preview_id: int, enabled: bool, index: int, delete: bool):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/preview/options/{type_}/{preview_id}'
        data = {
            "enabled": enabled,
            "index": index,
            "delete": delete
        }
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Массовое обновление статуса товаров
    # Bulk update products status
    def product_edit_v2(self, new_status: str, products: list):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/V2/status'
        data = {
            "new_status": new_status,
            "products": products
        }
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Массовое изменение цен товаров
    # Bulk update of product prices
    def product_edit_prices(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/prices'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Получение статуса выполнения асинхронной задачи
    # Getting the execution status of an asynchronous task
    def product_edit_update_products_tasks_status(self, task_id: str):
        params = {
            "token": self._get_valid_token(),
            "taskId": task_id
        }
        endpoint = f'product/edit/UpdateProductsTaskStatus'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Добавление товара в подкатегорию торговой площадки
    # Adding goods to the marketplace subcategory
    def product_platform_category_add(self, product_id: int, category_id: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/platform/category/add/{product_id}/{category_id}'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Получение дерева категорий торговой площадки
    # Getting the category tree of the marketplace
    def dictionary_platforms_categories(self, id_: str):
        endpoint = f'dictionary/platforms/categories/{id_}'
        return self._send_request('GET', self.URL + endpoint)

    # Получение подкатегорий торговой площадки
    # Getting the subcategories of the marketplace
    def dictionary_platforms_subcategories(self, id_: int):
        endpoint = f'dictionary/platforms/subcategories/{id_}'
        return self._send_request('GET', self.URL + endpoint)

    # Метод добавления содержимого типа "Файл"
    # The method of adding content of type "File"
    def product_content_add_file(self, product_id: int, file: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/content/add/file/{product_id}'
        return self._send_request('POST', self.URL + endpoint, files=file, params=params)

    # Метод добавления содержимого типа "Файл" с распаковкой ZIP-архива (до 200 файлов)
    # The method of adding content of type "File" from ZIP archive (max 200 files)
    def product_content_add_files(self, product_id: int, count: int, files: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/content/add/files/{product_id}/{count}'
        return self._send_request('POST', self.URL + endpoint, files=files, params=params)

    # Добавление содержимого типа "текст" или "ссылка"
    # The method of adding content of type "Text" and "Url"
    def product_content_add_text(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/content/add/text'
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Получение количества кодов, генерируемых Digiseller
    # Getting the number of codes generated by Digiseller
    def product_content_code_count_get(self, product_id: int, variant_id: Optional[int]):
        """
        :param variant_id: Variant ID. Specify None if you don't want the parameter to be passed. 0 is not allowed.
        :param product_id: Product ID. It is charming to point out.
        """
        params = {
            "token": self._get_valid_token(),
            "product_id": product_id,
            "variant_id": variant_id
        }
        endpoint = f'product/content/code/count'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Изменение количества кодов, генерируемых Digiseller
    # Change the number of codes generated by Digiseller
    def product_content_code_count_edit(self, product_id: int, variant_id: Optional[int], count: int):
        """
        :param variant_id: Variant ID. Specify None if you don't want the parameter to be passed. 0 is not allowed.
        :param product_id: Product ID. It is charming to point out.
        :param count: Amount of content for sale
        """
        params = {
            "token": self._get_valid_token(),
            "product_id": product_id,
            "variant_id": variant_id,
            "count": count
        }
        json_blat = {"count": count}
        endpoint = f'product/content/code/count'
        return self._send_request('PUT', self.URL + endpoint, params=params, data=json_blat)

    # Изменение количества генерируемых кодов Digiseller
    # Changing the number of generated codes by Digiseller
    def product_content_add_code(self, product_id: int, count: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/content/add/code/{product_id}/{count}'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Метод редактирования содержимого типа "Файл"
    # The method of updating content of type "File"
    def product_content_update_file_v2(self, files: dict, content_id: int, product_id: int, update_old: bool):
        params = {
            "token": self._get_valid_token(),
            "updateold": update_old,
            "productId": product_id, # Так с _ или без ?!
            "ContentId": content_id,
        }
        endpoint = 'product/content/update/file/v2'
        return self._send_request('POST', self.URL + endpoint, files=files, params=params)

    # Редактирование содержимого типа "текст" или "ссылка"
    # The method of updating content of type "Text" and "Url"
    def product_content_update_text(self, value: str, content_id: int, serial: str, update_old: bool, product_id: int):
        params = {"token": self._get_valid_token()}
        endpoint = 'product/content/update/text'
        data = {
            "serial": serial,
            "value": value,
            "update_old": update_old,  # Исправлено имя параметра
            "product_id": product_id,
            "content_id": content_id
        }
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Удаление содержимого типа "текст", "ссылка" или "файл"
    # The method of deleting content of type "text", "url" or "file"
    def product_content_delete(self, content_id: int, product_id: int):
        params = {
            "token": self._get_valid_token(),
            "contentId": content_id,
            "productId": product_id
        }
        endpoint = 'product/content/delete'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Полное удаление содержимого типа "текст", "ссылка" или "файл"
    # The method for completely deleting content of type "text", "url" or "file"
    def product_content_delete_all(self, product_id: int):
        params = {
            "token": self._get_valid_token(),
            "productId": product_id
        }
        endpoint = 'product/content/delete/all'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Создание или редактирование содержимого типа "форма"
    # The method of creating or updating content of type "form"
    def product_content_update_form(self, product_id: int, address: str, method: str, encoding: str, options: bool, answer: bool, allow_purchase_multiple_items: bool, url_for_quantity: str):
        params = {"token": self._get_valid_token()}
        endpoint = 'product/content/update/form'
        data = {
            "product_id": product_id,
            "address": address,
            "method": method,
            "encoding": encoding,
            "options": options,
            "answer": answer,
            "allow_purchase_multiple_items": allow_purchase_multiple_items
        }
        if url_for_quantity:
            data["url_for_quantity"] = url_for_quantity
        return self._send_request('POST', self.URL + endpoint, json=data, params=params)

    # Cоздание шаблона комиссионных отчислений
    # Create a commission template
    def templates(self, name: str):
        params = {"token": self._get_valid_token()}
        endpoint = f'templates'
        data = {"name": name}
        return self._send_request('POST', self.URL + endpoint, params=params, json=data)

    # Изменение шаблона комиссионных отчислений
    # Edit a commission template
    def templates_edit(self, name: str, id_: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'templates/{id_}'
        data = {"name": name}
        return self._send_request('POST', self.URL + endpoint, params=params, json=data)

    # Получение списка шаблонов отчислений
    # Get list of commission templates
    def templates_list(self, page: int, count: int):
        params = {
            "token": self._get_valid_token(),
            "page": page,
            "count": count
        }
        endpoint = f'templates'
        return self._send_request('GET', self.URL + endpoint, params=params)

    # Удаление шаблона комиссионных отчислений
    # Delete a commission template
    def templates_delete(self, id_: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'templates/delete/{id_}'
        return self._send_request('POST', self.URL + endpoint, params=params)     # Возвращает в случае успеха http 204

    # Получение списка товаров из шаблона отчислений
    # Getting the list of products from the deduction template
    def templates_products(self, template_id: int, product_id: int, price_min: float, price_max: float, currency: str,
                           language: str, name: str, min_comiss: float, max_comiss: float, in_affiliate: bool,
                           not_in_affiliate: bool, only_payment: bool, page: int, count: int):
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
            "token": self._get_valid_token()
        }
        endpoint = f'templates/products'
        return self._send_request('GET', self.URL + endpoint, params=params)