import hashlib
import time
from digiseller_api.request_handler import send_request

class DigisellerApi:
    URL = 'https://api.digiseller.ru/api/'
    def __init__(self, seller_id: str, api_key: str):
        if not isinstance(seller_id, str) or not seller_id:
            raise ValueError("Необходимо передать корректный 'seller_id'.")
        if not isinstance(api_key, str) or not api_key:
            raise ValueError("Необходимо передать корректный 'api_key'.")

        self.seller_id = int(seller_id)
        self.api_key = api_key
        self.token_expiration = 0
        self.token = None

    def _token_response(self):
        current_time = int(time.time())
        sign = hashlib.sha256((self.api_key + str(current_time)).encode()).hexdigest()
        data = {
            "seller_id": self.seller_id,
            "timestamp": current_time,
            "sign": sign
        }
        response = send_request('POST', self.URL + 'apilogin', json=data)
        return response

    def _get_token(self):
        current_time = int(time.time())
        token_validation = self._token_response()
        if token_validation.get('retval') == 0 and token_validation.get('token'):
            self.token = token_validation['token']
            self.token_expiration = current_time + 6600
            return self.token
        else:
            raise ValueError(f"Error obtaining authorization token on the server: {token_validation.get('desc')}")

    def _get_valid_token(self):
        if not self.token or int(time.time()) >= self.token_expiration:
            return self._get_token()
        return self.token

    # Поиск и проверка платежа по уникальному коду.
    def unique_code(self, unique_code):
        params = {"token": self._get_valid_token()}
        endpoint = f'purchases/unique-code/{unique_code}'
        return send_request('GET', self.URL + endpoint, params=params)

    # Информация о продаже по номеру заказа
    def purchase_info(self, invoice_id):
        params = {"token": self._get_valid_token()}
        endpoint = f'purchase/info/{invoice_id}'
        return send_request('GET', self.URL + endpoint, params=params)

    # Cписок последних продаж.
    def seller_last_sales(self, group=True, top=1000):
        params = {
            "token": self._get_valid_token(),
            "seller_id": self.seller_id,
            "group": group,
            "top": top
        }
        endpoint = 'seller-last-sales'
        return send_request('GET', self.URL + endpoint, params=params)

    # Статистика продаж.
    def seller_sells_statistic(self, product_ids: list, date_start: str, date_finish: str, returned: int, page: int, rows: int):
        params = {
            "token": self._get_valid_token(),
        }
        data = {
            "product_ids": product_ids,
            "date_start": date_start,
            "date_finish": date_finish,
            "returned": returned,
            "page": page,
            "rows": rows
        }
        endpoint = 'seller-sells/v2'
        return send_request('POST', self.URL + endpoint, params=params, json=data)

    # Статистика продаж в роли агента.
    def agent_sales_statistic(self, product_ids: list, date_start: str, date_finish: str, returned: int, page: int, rows: int):
        params = {
            "token": self._get_valid_token(),
        }
        data = {
            "product_ids": product_ids,
            "date_start": date_start,
            "date_finish": date_finish,
            "returned": returned,
            "page": page,
            "rows": rows
        }
        endpoint = 'agent-sales/v2'
        return send_request('POST', self.URL + endpoint, params=params, json=data)

    # Список категорий (каталог).
    def categories_list(self, category_id: int, lang: str):
        params = {
            "seller_id": self.seller_id,
            "category_id": category_id,
            "lang": lang
        }
        endpoint = f'categories'
        return send_request('GET', self.URL + endpoint, params=params)

    # Список товаров из категории.
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
        return send_request('GET', self.URL + endpoint, params=params)

    # Быстрое получение описаний товаров по списку ID.
    def products_list_description(self, ids: list, lang: str, use_token = True):
        data = {
            "ids": ids,
            "lang": lang,
        }
        if use_token:
            data["token"] = self._get_valid_token()
        endpoint = f'products/list'
        return send_request('POST', self.URL + endpoint, json=data)

    # Описание товара.
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
        return send_request('GET', self.URL + endpoint, params=params)

    # Получение цены с учетом входящих значений параметров и/или количества товара.
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
        return send_request('GET', self.URL + endpoint, params=params)

    # Отзывы о товарах.
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
        return send_request('GET', self.URL + endpoint, params=params)

    # Товары продавца.
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
        return send_request('POST', self.URL + endpoint, json=data, params = params)

    @staticmethod
    # Скидка по товару.
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
        return send_request('POST', url, data=xml_data)

    @staticmethod
    # Поиск по товарам.
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
        return send_request('POST', url, data=xml_data)

    # Создание копии описания товара (клонирование без содержимого).
    def product_clone(self, product_id: int, count: int, categories: bool, notify: bool, discounts: bool, options: bool, comissions: bool, gallery: bool):
        data = {
            "count": count,
            "categories": categories,
            "notify": notify,
            "discounts": discounts,
            "options": options,
            "comissions": comissions,
            "gallery": gallery
        }
        params = {"token": self._get_valid_token()}
        endpoint = f'product/clone/{product_id}'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Список товаров продавца с индивидуальным предложением.
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
        return send_request('GET', self.URL + endpoint, params=params)

    # Создание товара типа "Уникальный товар с фиксированной ценой".
    def product_create_uniquefixed(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/create/uniquefixed'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Создание товара типа "Уникальный товар с нефиксированной ценой".
    def product_create_uniqueunfixed(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/create/uniqueunfixed'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Создание товара типа "Электронная книга".
    def product_create_book(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/create/book'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Создание товара типа "Программное обеспечение".
    def product_create_software(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/create/software'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Создание товара типа "Произвольный цифровой товар".
    def product_create_arbitrary(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/create/arbitrary'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование товара типа "Уникальный товар с фиксированной ценой".
    def product_edit_uniquefixed(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/uniquefixed/{product_id}'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование товара типа "Уникальный товар с нефиксированной ценой"
    def product_edit_uniqueunfixed(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/uniqueunfixed/{product_id}'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование товара типа "Электронная книга".
    def product_edit_book(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/book/{product_id}'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование товара типа "Программное обеспечение".
    def product_edit_software(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/software/{product_id}'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование товара типа "Произвольный цифровой товар".
    def product_edit_arbitrary(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/arbitrary/{product_id}'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование базовых свойств товара. Включение / выключение товара.
    def product_edit_base(self, product_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/base/{product_id}'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Добавление изображений товара.
    def product_preview_add_images(self, product_id: int, files: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'preview/add/images/{product_id}'
        return send_request('POST', self.URL + endpoint, files=files, params=params)

    # Добавление youtube-ссылок в галерею.
    def product_preview_add_videos(self, product_id: int, urls: list):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/preview/add/videos/{product_id}'
        data = {"urls": urls}
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Изменение позиции и удаление изображений в галерее.
    def product_preview_options(self, type_: str, preview_id: int, enabled: bool, index: int, delete: bool):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/preview/options/{type_}/{preview_id}'
        data = {
            "enabled": enabled,
            "index": index,
            "delete": delete
        }
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Массовое обновление статуса товаров.
    def product_edit_v2(self, new_status: str, products: list):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/V2/status'
        data = {
            "new_status": new_status,
            "products": products
        }
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Добавление товара в подкатегорию торговой площадки.
    def product_platform_category_add(self, product_id: int, category_id: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/platform/category/add/{product_id}/{category_id}'
        return send_request('GET', self.URL + endpoint, params=params)

    # Получение дерева категорий торговой площадки.
    def dictionary_platforms_categories(self, id_: str):
        endpoint = f'dictionary/platforms/categories/{id_}'
        return send_request('GET', self.URL + endpoint)

    # Получение подкатегорий торговой площадки.
    def dictionary_platforms_subcategories(self, id_: int):
        endpoint = f'dictionary/platforms/subcategories/{id_}'
        return send_request('GET', self.URL + endpoint)

    # Массовое изменение цен товаров.
    def product_edit_prices(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/edit/prices'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Получение статуса выполнения асинхронной задачи.
    def product_edit_update_products_tasks_status(self, task_id: str):
        params = {
            "token": self._get_valid_token(),
            "taskId": task_id
        }
        endpoint = f'product/edit/UpdateProductsTaskStatus'
        return send_request('GET', self.URL + endpoint, params=params)

    # Метод добавления содержимого типа "Файл".
    def product_content_add_file(self, product_id: int, file: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/content/add/file/{product_id}'
        return send_request('POST', self.URL + endpoint, files=file, params=params)

    # Метод добавления содержимого типа "Файл" с распаковкой ZIP-архива (до 200 файлов).
    def product_content_add_files(self, product_id: int, count: int, files: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/content/add/files/{product_id}/{count}'
        return send_request('POST', self.URL + endpoint, files=files, params=params)

    # Добавление содержимого типа "текст" или "ссылка".
    def product_content_add_text(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/content/add/text'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Изменение количества генерируемых кодов Digiseller.
    def product_content_add_code(self, product_id: int, count: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/content/add/code/{product_id}/{count}'
        return send_request('GET', self.URL + endpoint, params=params)

    # Метод редактирования содержимого типа "Файл".
    def product_content_update_file_v2(self, files: dict, content_id: int, product_id: int, update_old: bool):
        params = {"token": self._get_valid_token()}
        if product_id is None:
            params.update({
                "contentid": content_id,
                "updateold": update_old,
            })
        else:
            params.update({
                "contentid": product_id,
                "updateold": update_old,
            })
        endpoint = f'product/content/update/file/v2'
        return send_request('POST', self.URL + endpoint, files=files, params=params)

    # Редактирование содержимого типа "текст" или "ссылка".
    def product_content_update_text(self, content_id: int, serial: str, value: str, update_old: bool, product_id: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/content/update/text'
        data = {
            "serial": serial,
            "value": value,
            "updateold": update_old,
        }
        if product_id is None:
            data.update({
                "content_id": content_id
            })
        else:
            data.update({
                "product_id": product_id
            })
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Удаление содержимого типа "текст", "ссылка" или "файл".
    def product_content_delete(self, content_id: int, product_id: int):
        params = {
            "token": self._get_valid_token(),
            "contentid": content_id,
            "productid": product_id
        }
        endpoint = f'product/content/delete'
        return send_request('GET', self.URL + endpoint, params=params)

    # Полное удаление содержимого типа "текст", "ссылка" или "файл".
    def product_content_delete_all(self, product_id: int):
        params = {
            "token": self._get_valid_token(),
            "productid": product_id
        }
        endpoint = f'product/content/delete/all'
        return send_request('GET', self.URL + endpoint, params=params)

    # Создание или редактирование содержимого типа "форма".
    def product_content_update_form(self, product_id: int, address: str, method: str, encoding: str, options: bool, answer: bool, allow_purchase_multiple_items: bool, url_for_quantity: str):
        params = {"token": self._get_valid_token()}
        endpoint = f'product/content/update/form'
        data = {
            "product_id": product_id,
            "address": address,
            "method": method,
            "encoding": encoding,
            "options": options,
            "answer": answer,
            "allow_purchase_multiple_items": allow_purchase_multiple_items,
            "url_for_quantity": url_for_quantity
        }
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Cоздание шаблона комиссионных отчислений.
    def templates(self, name: str):
        params = {"token": self._get_valid_token()}
        endpoint = f'templates'
        data = {"name": name}
        return send_request('POST', self.URL + endpoint, params=params, json=data)

    # Изменение шаблона комиссионных отчислений.
    def templates_edit(self, name: str, id_: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'templates/{id_}'
        data = {"name": name}
        return send_request('POST', self.URL + endpoint, params=params, json=data)

    # Получение списка шаблонов отчислений.
    def templates_list(self, page: int, count: int):
        params = {
            "token": self._get_valid_token(),
            "page": page,
            "count": count
        }
        endpoint = f'templates'
        return send_request('GET', self.URL + endpoint, params=params)

    # Удаление шаблона комиссионных отчислений.
    def templates_delete(self, id_: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'templates/delete/{id_}'
        return send_request('POST', self.URL + endpoint, params=params)

    # Получение списка товаров из шаблона отчислений.
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
        return send_request('GET', self.URL + endpoint, params=params)

    # Обновление товаров в шаблоне отчислений.
    def update_template_products(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'templates/products'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Применение шаблона отчислений.
    def template_apply(self, template_id: int, seller_id: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'templates/apply'
        data = {
            "template_id": template_id,
            "seller_id": seller_id
        }
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Список параметров товара.
    def products_options_list(self, product_id: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'products/options/list/{product_id}'
        return send_request('GET', self.URL + endpoint, params=params)

    # Информация о параметре.
    def products_options_info(self, option_id: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'products/options/{option_id}'
        return send_request('GET', self.URL + endpoint, params=params)

    # Создание параметра.
    def products_options_add(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'products/options'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование параметра.
    def products_options_update(self, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'products/options/update'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Удаление параметра.
    def products_options_delete(self, option_id: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'products/options/{option_id}/delete'
        return send_request('GET', self.URL + endpoint, params=params)

    # Создание варианта.
    def products_variant_add(self, option_id: int, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'products/options/{option_id}/variants'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Редактирование варианта.
    def products_variant_edit(self, option_id: int, variants: list, data: dict):
        params = {"token": self._get_valid_token()}
        endpoint = f'products/options/{option_id}/variants/{variants}'
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Удаление варианта.
    def products_variant_delete(self, option_id: int, variant_id: int):
        params = {"token": self._get_valid_token()}
        endpoint = f'products/options/{option_id}/variants/{variant_id}/delete'
        return send_request('GET', self.URL + endpoint, params=params)

    # Получение списка диалогов.
    def chat_list(self, filter_new: int, email: str, id_ds: list, pagesize: int, page: int):
        params = {
            "token": self._get_valid_token(),
            'filter_new': filter_new,
            'email': email,
            'id_ds': id_ds,
            'pagesize': pagesize,
            'page': page
        }
        endpoint = f'debates/v2/chats'
        return send_request('GET', self.URL + endpoint, params=params)

    # Получение статуса диалога.
    def chat_status(self, order_id: int):
        params = {
            "token": self._get_valid_token(),
            "id_i": order_id
        }
        endpoint = f'debates/v2/chat-state'
        return send_request('GET', self.URL + endpoint, params=params)

    # Изменение статуса диалога.
    def chat_edit_status(self, order_id: int, chat_state: int):
        params = {
            "token": self._get_valid_token(),
            "id_i": order_id,
            "chat_state": chat_state
        }
        endpoint = f'debates/v2/chat-state'
        return send_request('POST', self.URL + endpoint, params=params)

    # Получение списка сообщений.
    def chat_order_messages(self, order_id: int, hidden: int, id_from: int, id_to: int, old_id: int, newer: int, count: int):
        params = {
            "token": self._get_valid_token(),
            "id_i": order_id,
            "hidden": hidden,
            "id_from": id_from,
            "id_to": id_to,
            "old_id": old_id,
            "newer": newer,
            "count": count
        }
        endpoint = f'debates/v2'
        return send_request('GET', self.URL + endpoint, params=params)

    # Установка флага прочитан.
    def chat_set_flag(self, order_id: int):
        params = {
            "token": self._get_valid_token(),
            "id_i": order_id
        }
        endpoint = f'debates/v2/seen'
        return send_request('POST', self.URL + endpoint, params=params)

    # Предварительная загрузка файлов.
    def chat_upload_preview(self, files: dict, lang: str):
        params = {
            "token": self._get_valid_token(),
            "lang": lang
        }
        endpoint = f'debates/v2/upload-preview'
        return send_request('POST', self.URL + endpoint, params=params, files=files)

    # Отправка нового сообщения.
    def chat_send_message(self, order_id: int, data: dict):
        params = {
            "token": self._get_valid_token(),
            "id_i": order_id
        }
        endpoint = f'debates/v2'
        return send_request('POST', self.URL + endpoint, params=params, json=data)

    # Удаление сообщения.
    def chat_delete_message(self, order_id: int, message_id: int):
        params = {
            "token": self._get_valid_token(),
            "id_i": order_id
        }
        endpoint = f'debates/v2/{message_id}'
        return send_request('DELETE', self.URL + endpoint, params=params)

    # Получение списка сообщений.
    def chat_admin_messages(self, date_from: str, count: int, id_from: int, id_to: int, corr_id: int, only_unread: bool):
        params = {
            "token": self._get_valid_token(),
            "date_from": date_from,
            "count": count,
            "id_from": id_from,
            "id_to": id_to,
            "corr_id": corr_id,
            "only_unread": only_unread
        }
        endpoint = f'messages/v2'
        return send_request('GET', self.URL + endpoint, params=params)

    # Получение текущих значений валют
    def exchange_rate(self, base_currency: str):
        params = {
            "token": self._get_valid_token(),
            "base_currency": base_currency
        }
        endpoint = f'sellers/currency'
        return send_request('GET', self.URL + endpoint, params=params)

    # Изменение курса валют.
    def change_exchange_rate(self, base_currency: str, rate: float, bank: str, complement: float, type_currency: str):
        params = {"token": self._get_valid_token()}
        endpoint = f'sellers/currency'
        data = {
            "base_currency": base_currency,
            "rate": rate,
            "bank": bank,
            "complement": complement,
            "type_currency": type_currency
        }
        return send_request('POST', self.URL + endpoint, json=data, params=params)

    # Реклама на площадке.
    def advertisement(self, owner: int, date: str, lang: str):
        params = {
            "token": self._get_valid_token(),
            "owner": owner,
            "date": date,
            "lang": lang
        }
        endpoint = f'rekl'
        return send_request('GET', self.URL + endpoint, params=params)