# Digiseller API Python

[![PyPI version](https://img.shields.io/pypi/v/digiseller-api-python.svg)](https://pypi.org/project/digiseller-api-python)
[![Downloads](https://img.shields.io/pypi/dm/digiseller-api-python)](https://pypistats.org/packages/digiseller-api-python)
[![License](https://img.shields.io/github/license/Ernieleo/digiseller-api-python)](https://github.com/Ernieleo/digiseller-api-python/blob/main/LICENSE)

Digiseller API Python — это библиотека Python для доступа к API Digiseller. 

Добавлено 70 методов из числа представленных в документации.

**Важное примечание**: Данный проект не является официальным.  
Я не имею никакого отношения к команде разработчиков сервиса Digiseller.  

Возможны ошибки в некоторых запросах, так как комплексное тестирование не проводилось.  
Часть запросов из документации на сайте Digiseller не соответствуют действительности.  

Ознакомиться с документацией API вы можете на [сайте Digiseller](https://my.digiseller.com/inside/api.asp)

## Установка

Вы можете установить с сервиса [PyPI](https://pypi.org/project/digiseller-api-python/)

```sh
pip install digiseller-api-python
```

## Простая демонстрация
```python
from digiseller_api_python import Api

Digiseller_Api = Api(seller_id="11155533", api_key="CA1SF69A000A46D00039F01Z11017V39")

# Получение данных пользователя указанных при заказе по уникальному коду
def get_account_info_from_digiseller(unique_code):
    data = Digiseller_Api.unique_code(unique_code)
    email = None
    password = None

    for option in data["options"]:
        if option["name"] in ["Почта аккаунта ChatGPT", "ChatGPT account email"]:
            email = option["value"]
        elif option["name"] in ["Пароль аккаунта ChatGPT", "ChatGPT account password"]:
            password = option["value"]

    return email, password
```

Используется для получения логина и пароля указанных покупателем при оформлении заказа в полях ввода (Параметры) текстовых данных. Поиск требуемого поля осуществляется по названию, указывается названия поля на двух языках, название поля параметра полученного в сведениях о заказе по уникальному коду, зависит от языка браузера пользователя.

## Разработка
Любой вклад в проект приветствуется.  
Если вы хотите помочь в разработке, следуйте правилам API сервиса Digiseller и придерживайтесь общего стиля кода. Создайте запрос на cлияние и я его рассмотрю!

## Доступные методы API
Cписок был сгенерирован при помощи ChatGPT, возможны неточности.  
Каждая функция вызова описана в самом коде, смотрите информацию в IDE. 

Параметры запросов с документации API, значения соответствуют.
1. Название: `Поиск и проверка платежа по уникальному коду`
    - Функция: `unique_code`
    - Параметры: `unique_code: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_general.asp#searchuniquecode)

2. Название: `Информация о продаже по номеру заказа`
    - Функция: `purchase_info`
    - Параметры: `invoice_id: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_general.asp#purchase_info)

3. Название: `Список последних продаж`
    - Функция: `seller_last_sales`
    - Параметры: `group: bool, top: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_statistics.asp#last_sales)

4. Название: `Статистика продаж`
    - Функция: `seller_sells_statistic`
    - Параметры: `product_ids: list, date_start: str, date_finish: str, returned: int, page: int, rows: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_statistics.asp#statisticsells)

5. Название: `Статистика продаж в роли агента`
    - Функция: `agent_sales_statistic`
    - Параметры: `product_ids: list, date_start: str, date_finish: str, returned: int, page: int, rows: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_statistics.asp#statistics_agent_sales)

6. Название: `Список категорий (каталог)`
    - Функция: `categories_list`
    - Параметры: `category_id: int, lang: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_catgoods.asp#categories)

7. Название: `Список товаров из категории`
    - Функция: `shop_products`
    - Параметры: `category_id: int, page: int, rows: int, order: str, currency: str, lang: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_catgoods.asp#products)

8. Название: `Быстрое получение описаний товаров по списку ID`
    - Функция: `products_description`
    - Параметры: `ids: list, lang: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_catgoods.asp#products_list)

9. Название: `Описание товара`
    - Функция: `product_description`
    - Параметры: `product_id: int, seller_id: int, partner_uid: str, currency: str, lang: str, owner: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_catgoods.asp#product_info)

10. Название: `Получение цены с учетом входящих значений параметров и/или количества товара`
    - Функция: `products_price_calc`
    - Параметры: `product_id: int, options: str, currency: str, amount: int, unit_cnt: int, count: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_catgoods.asp#products_price_calc)

11. Название: `Отзывы о товарах`
    - Функция: `product_reviews`
    - Параметры: `seller_id: int, product_id: int, type_: str, owner_id: int, page: int, rows: int, lang: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_catgoods.asp#reviews)

12. Название: `Товары продавца`
    - Функция: `seller_goods`
    - Параметры: `seller_id: int, order_col: str, order_dir: str, rows: int, page: int, currency: str, lang: str, show_hidden: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_catgoods.asp#seller-goods)

13. Название: `Создание копии описания товара (клонирование без содержимого)`
    - Функция: `product_clone`
    - Параметры: `product_id: int, count: int, categories: bool, notify: bool, discounts: bool, options: bool, comissions: bool, gallery: bool`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_catgoods.asp#copyproduct)

14. Название: `Список товаров продавца с индивидуальным предложением`
    - Функция: `agents_offer`
    - Параметры: `seller_id: int, product_name: str, product_id: int, only_in_stock: bool, only_individual: bool, page: int, count: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_catgoods.asp#goodswithoffer)

15. Название: `Создание товара типа "Уникальный товар с фиксированной ценой"`
    - Функция: `product_create_uniquefixed`
    - Параметры: `data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#createuniquefixed)

16. Название: `Создание товара типа "Уникальный товар с нефиксированной ценой"`
    - Функция: `product_create_uniqueunfixed`
    - Параметры: `data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#createuniqueunfixed)

17. Название: `Создание товара типа "Электронная книга"`
    - Функция: `product_create_book`
    - Параметры: `data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#createbook)

18. Название: `Создание товара типа "Программное обеспечение"`
    - Функция: `product_create_software`
    - Параметры: `data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#createsoftware)

19. Название: `Создание товара типа "Произвольный цифровой товар"`
    - Функция: `product_create_arbitrary`
    - Параметры: `data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#createarbitrary)

20. Название: `Редактирование товара типа "Уникальный товар с фиксированной ценой"`
    - Функция: `product_edit_uniquefixed`
    - Параметры: `product_id: int, data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#edituniquefixed)

21. Название: `Редактирование товара типа "Уникальный товар с нефиксированной ценой"`
    - Функция: `product_edit_uniqueunfixed`
    - Параметры: `product_id: int, data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#edituniqueunfixed)

22. Название: `Редактирование товара типа "Электронная книга"`
    - Функция: `product_edit_book`
    - Параметры: `product_id: int, data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#editbook)

23. Название: `Редактирование товара типа "Программное обеспечение"`
    - Функция: `product_edit_software`
    - Параметры: `product_id: int, data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#editsoftware)

24. Название: `Редактирование товара типа "Произвольный цифровой товар"`
    - Функция: `product_edit_arbitrary`
    - Параметры: `product_id: int, data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#editarbitrary)

25. Название: `Редактирование базовых свойств товара. Включение/выключение товара`
    - Функция: `product_edit_base`
    - Параметры: `product_id: int, data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#editbase)

26. Название: `Добавление изображений товара`
    - Функция: `product_preview_add_images`
    - Параметры: `product_id: int, files`
    - Примечание: `Files: {'image.jpeg': open('pic.jpeg', 'rb')}`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#add_image_preview)

27. Название: `Добавление youtube-ссылок в галерею`
    - Функция: `product_preview_add_videos`
    - Параметры: `product_id: int, files`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#add_video_preview)

28. Название: `Изменение позиции и удаление изображений в галерее`
    - Функция: `product_preview_options`
    - Параметры: `type_: str, preview_id: int, enabled: bool, index: int, delete: bool`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#preview_options)

29. Название: `Массовое обновление статуса товаров`
    - Функция: `product_edit_v2`
    - Параметры: `new_status: str, products: list`
    - Примечание: `(list): ID товаров. Не более 200 товаров в 1 запросе: ["123", "345"]`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#change_status)

30. Название: `Добавление товара в подкатегорию торговой площадки`
    - Функция: `product_platform_category_add`
    - Параметры: `product_id: int, platforms: list`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#producttomarketplacesubcategory)

31. Название: `Получение дерева категорий торговой площадки`
    - Функция: `dictionary_platforms_categories`
    - Параметры: `id_: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#marketplacecategories)

32. Название: `Получение подкатегорий торговой площадки`
    - Функция: `dictionary_platforms_subcategories`
    - Параметры: `id_: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#marketplacesubcategories)

33. Название: `Массовое изменение цен товаров`
    - Функция: `product_edit_prices`
    - Параметры: `data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#massPriceUpdate)

34. Название: `Получение статуса выполнения асинхронной задачи`
    - Функция: `product_edit_update_products_tasks_status`
    - Параметры: `task_id: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_goods.asp#productsUpdateStatus)

35. Название: `Метод добавления содержимого типа "Файл"`
    - Функция: `product_content_add_file`
    - Параметры: `product_id: int, file`
    - Примечание: `File: files = {'text.txt': open('passwords.txt', 'rb')}`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_content.asp#addfile)

36. Название: `Метод добавления содержимого типа "Файл" с распаковкой ZIP-архива (до 200 файлов)`
    - Функция: `product_content_add_files`
    - Параметры: `product_id: int, count: int, files`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_content.asp#addfiles)

37. Название: `Добавление содержимого типа "текст" или "ссылка"`
    - Функция: `product_content_add_text`
    - Параметры: `data: dict`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_content.asp#addtext)

38. Название: `Изменение количества генерируемых кодов Digiseller`
    - Функция: `product_content_add_code`
    - Параметры: `product_id: int, count: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_content.asp#addcode)

39. Название: `Метод редактирования содержимого типа "Файл"`
    - Функция: `product_content_update_file_v2`
    - Параметры: `files: dict, content_id: int, product_id: int, update_old: bool`
    - Примечание: `files = { '1': ('image1.jpeg', open('1.jpeg', 'rb')), '2': ('image2.jpeg', open('2.jpeg', 'rb')) }`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_content.asp#updateFile)

40. Название: `Редактирование содержимого типа "текст" или "ссылка"`
    - Функция: `product_content_update_text`
    - Параметры: `content_id: int, serial: str, value: str, update_old: bool, product_id: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_content.asp#updateText)

41. Название: `Удаление содержимого типа "текст", "ссылка" или "файл"`
    - Функция: `product_content_delete`
    - Параметры: `content_id: int, product_id: int`
    - Ответ: `StatusCode: 204 (NoContent)`
    - [Ссылка на API](https://my.digiseller.com/inside/api_content.asp#deleteContent)

42. Название: `Полное удаление содержимого типа "текст", "ссылка" или "файл"`
    - Функция: `product_content_delete_all`
    - Параметры: `product_id: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_content.asp#deleteAllContent)

43. Название: `Создание или редактирование содержимого типа "форма"`
    - Функция: `product_content_update_form`
    - Параметры: `product_id: int, address: str, method: str, encoding: str, options: bool, answer: bool, allow_purchase_multiple_items: bool, url_for_quantity: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_content.asp#update_form)

44. Название: `Cоздание шаблона комиссионных отчислений`
    - Функция: `templates`
    - Параметры: `name: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_templates.asp#create_template)

45. Название: `Изменение шаблона комиссионных отчислений`
    - Функция: `templates_edit`
    - Параметры: `name: str, id_: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_templates.asp#edit_template)

46. Название: `Получение списка шаблонов отчислений`
    - Функция: `templates_list`
    - Параметры: `page: int, count: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_templates.asp#get_list_templates)

47. Название: `Удаление шаблона комиссионных отчислений`
    - Функция: `templates_delete`
    - Параметры: `id_: int, method: str = "POST"`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_templates.asp#delete_template)

48. Название: `Получение списка товаров из шаблона отчислений`
    - Функция: `templates_products`
    - Параметры: `template_id: int, product_id: int, price_min: float, price_max: float, currency: str, language: str, name: str, min_comiss: float, max_comiss: float, in_affiliate: bool, not_in_affiliate: bool, only_payment: bool, page: int, count: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_templates.asp#get_products)

49. Название: `Обновление товаров в шаблоне отчислений`
    - Функция: `update_template_products`
    - Параметры: `data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `StatusCode: 204 (NoContent)`
    - [Ссылка на API](https://my.digiseller.com/inside/api_templates.asp#edit_products)

50. Название: `Применение шаблона отчислений`
    - Функция: `template_apply`
    - Параметры: `template_id: int, seller_id: int`
    - Ответ: `StatusCode: 204 (NoContent)`
    - [Ссылка на API](https://my.digiseller.com/inside/api_templates.asp#apply)

51. Название: `Список параметров товара`
    - Функция: `products_options_list`
    - Параметры: `product_id: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_parameters.asp#getlist)

52. Название: `Информация о параметре`
    - Функция: `products_options_info`
    - Параметры: `option_id: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_parameters.asp#getfull)

53. Название: `Создание параметра`
    - Функция: `products_options_add`
    - Параметры: `name_ru: str, name_en: str, comment_ru: str, comment_en: str, ptype: str, separate_content: bool, required: bool, modifier_visible: bool, order: int, product_id: int, variant_dict: dict`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_parameters.asp#createparam)

54. Название: `Редактирование параметра`
    - Функция: `products_options_update`
    - Параметры: `name_ru: str, name_en: str, ptype: str, separate_content: bool, required: bool, modifier_visible: bool, order: int, option_id: int, comment_ru: str, comment_en: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_parameters.asp#editparam)

55. Название: `Удаление параметра`
    - Функция: `products_options_delete`
    - Параметры: `option_id: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_parameters.asp#deleteparam)

56. Название: `Создание варианта`
    - Функция: `products_variant_add`
    - Параметры: `option_id: int, data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_parameters.asp#createvariant)

57. Название: `Редактирование варианта`
    - Функция: `products_variant_edit`
    - Параметры: `option_id: int, variant_id: int, name_ru: str, name_en: str, ptype: str, rate: int, default: bool, visible: bool, order: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_parameters.asp#editvariant)

58. Название: `Удаление варианта`
    - Функция: `products_variant_delete`
    - Параметры: `option_id: int, variant_id: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_parameters.asp#deletevariant)

59. Название: `Получение списка диалогов`
    - Функция: `chat_list`
    - Параметры: `filter_new: int, email: str, id_ds: str, pagesize: int, page: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_debates.asp#get_chats)

60. Название: `Получение статуса диалога`
    - Функция: `chat_status`
    - Параметры: `id_i: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_debates.asp#get_state)

61. Название: `Изменение статуса диалога`
    - Функция: `chat_edit_status`
    - Параметры: `id_i: int, chat_state: int`
    - Ответ: `'StatusCode: 200 (NoContent)'`
    - [Ссылка на API](https://my.digiseller.com/inside/api_debates.asp#post_state)

62. Название: `Получение списка сообщений`
    - Функция: `chat_order_messages`
    - Параметры: `id_i: int, hidden: int, id_from: int, id_to: int, old_id: int, newer: int, count: int`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_debates.asp#get_debates)

63. Название: `Установка флага прочитан`
    - Функция: `chat_set_flag`
    - Параметры: `id_i: int`
    - Ответ: `StatusCode: 200 (NoContent)`
    - [Ссылка на API](https://my.digiseller.com/inside/api_debates.asp#post_seen)

64. Название: `Предварительная загрузка файлов`
    - Функция: `chat_upload_preview`
    - Параметры: `files, lang: str`
    - Примечание: `Files: [('files[]', ('file': open(file_path, 'rb'))]`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_debates.asp#upload_preview-)

65. Название: `Отправка нового сообщения`
    - Функция: `chat_send_message`
    - Параметры: `id_i: int, data: dict`
    - Примечание: `Формат запроса (Data) указан в Документации API. См. Ссылка на API`
    - Ответ: `StatusCode: 200 (NoContent)`
    - [Ссылка на API](https://my.digiseller.com/inside/api_debates.asp#post_debate)

66. Название: `Удаление сообщения`
    - Функция: `chat_delete_message`
    - Параметры: `order_id: int, message_id: int`
    - Ответ: `[] (NoContent)`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_debates.asp#delete_debate)

67. Название: `Реклама на площадке`
    - Функция: `rekl`
    - Параметры: `owner: int, date: str, lang: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_rekl.asp#rekl)

68. Название: `Операции по личному счету Digiseller`
    - Функция: `sellers_account_receipts`
    - Параметры: `page: int, count: int, currency: str, types: list, code_filter: str, allowtype: str, start: str, finish: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_account.asp#digiseller)

69. Название: `Операции через внешних агрегаторов`
    - Функция: `sellers_account_receipts_external`
    - Параметры: `page: int, count: int, order: str, code: str, aggregator: str`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_account.asp#external)

70. Название: `Информация о балансе личного счёта`
    - Функция: `sellers_account_balance`
    - Параметры: `Передача не требуется`
    - Ответ: `Ответ от сервера в формате JSON`
    - [Ссылка на API](https://my.digiseller.com/inside/api_account.asp#view_balance)
