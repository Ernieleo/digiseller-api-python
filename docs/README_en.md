<p align="center">
  <img src="https://i.ibb.co/hyTLSDZ/digiseller-logo.png" alt="Digiseller API Python" width="80%">
</p>

[![PyPI version](https://img.shields.io/pypi/v/digiseller-api-python.svg?cacheSeconds=3600)](https://pypi.org/project/digiseller-api-python)
[![PyPI Package Monthly Download](https://img.shields.io/pypi/dm/digiseller-api-python)](https://pypistats.org/packages/digiseller-api-python)
[![License](https://img.shields.io/github/license/Ernieleo/digiseller-api-python)](https://github.com/Ernieleo/digiseller-api-python/blob/master/LICENSE)
[![Test Status](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/test.yml/badge.svg)](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/release_pypi.yml)

**Digiseller API Python** is an unofficial Python library for interacting with the Digiseller API.

**Important note**: This project is not affiliated with the official Digiseller development team and is not an official library.  
There may be inaccuracies in some requests, as comprehensive testing has not been conducted. Some API methods described in Digiseller's documentation may not behave as documented.

Full API documentation can be found on the [Digiseller website](https://my.digiseller.com/inside/api.asp).  
The API methods for buyers from the "Payment" section are not included in the library.

## ⚠️ Import change (since version 3.0.0)

Starting from **version 3.0.0**, the library uses a new internal structure.  
You must now import from `digiseller_api_python` instead of `digiseller_api`.

### Before (up to 3.0.0):
```python
from digiseller_api import DigisellerApi
```
### Now (since 3.0.0):
```python
from digiseller_api_python import DigisellerApi
```

---

## Installation

### Using PyPI:
```sh
pip install digiseller-api-python
```

### Installing from GitHub repository:
```sh
pip3 install git+https://github.com/Ernieleo/digiseller-api-python.git
```

## Usage example

To use the Digiseller API, you will need an `API key` and a `Seller ID`:

- Get your **API key** [here](https://my.digiseller.com/inside/api_keys.asp)
- Get your **Seller ID** [here](https://my.digiseller.com/)

Keep your API key secure. Do not publish it online.

### Code example

```python
from digiseller_api_python import DigisellerApi

# Create API client instance
digiseller_api = DigisellerApi(seller_id="11155533", api_key="ZA1SG0YDA46DV0Z39F01Z11017V39")


# Example function to retrieve user-entered order data using a unique code
def get_account_info_from_digiseller(unique_code):
    email, password = None, None
    try:
        # Send request
        data = digiseller_api.unique_code(unique_code)

        # Extract required fields
        for option in data.get("options", []):
            if option["name"] in ["Почта аккаунта ChatGPT", "ChatGPT account email"]:
                email = option["value"]
            elif option["name"] in ["Пароль аккаунта ChatGPT", "ChatGPT account password"]:
                password = option["value"]

        return email, password
    except Exception as e:
        print(f"Error: {e}")
        return None, None


# Using the function to retrieve data
unique_code = "YOUR_UNIQUE_CODE"
email, password = get_account_info_from_digiseller(unique_code)
print("Email:", email)
print("Password:", password)
```

This example demonstrates how to use `DigisellerApi` to retrieve data entered by the customer when placing an order.  
The `get_account_info_from_digiseller` function queries by unique code and looks for fields in multiple possible languages.

### Additional example

```python
from digiseller_api_python import DigisellerApi

from PIL import Image
from io import BytesIO

image = DigisellerApi.get_main_img(id_d=4470041, maxlength=400)
image_bytes = image.encode() if isinstance(image, str) else image
image = Image.open(BytesIO(image_bytes))
image.show()
```

This example demonstrates using the [product main image retrieval function](https://my.digiseller.com/inside/api_catgoods.asp#fast_image)  
The function does not require seller credentials or creating a client instance.

### Response formats

- **JSON (`application/json`)** → Python `dict`
- **XML (`application/xml`, `text/xml`)** → string
- **Image (`image/*`)** → bytes object
- **Text (`text/plain` and others)** → string
- **Other types** → raw status code

## Error handling

The library defines its own exception classes for more accurate error control.

### Base exception

```python
from digiseller_api_python import DigisellerError
```

All exceptions inherit from `DigisellerError`, so you can catch specific or general errors:

```python
try:
    digiseller_api.get_token()
except DigisellerError as e:
    print(f"Digiseller API Error: {e}")
```

---

### Available exceptions

| Exception                         | Description                                 |
|----------------------------------|---------------------------------------------|
| `DigisellerError`                | Base exception                              |
| `DigisellerTimeoutError`         | Request timed out                           |
| `DigisellerInvalidResponseError` | API returned malformed or unexpected data   |
| `DigisellerHTTPError`            | HTTP error (e.g. 400, 500, etc.)            |

---

You can use these exceptions for logging, debugging, or graceful fallbacks.

## Development

Contributions are welcome!  
If you'd like to help maintain or improve the project, please follow Digiseller’s official API rules and keep consistent coding style.

To contribute, fork the repo, make your changes, and submit a pull request.

## Planned

In the future: full documentation and improved usability.

- [x] Add all API functions
- [x] Additional usage example in Python
- [x] Add missing API methods
- [ ] Full method documentation (in progress)
- [x] Add remaining methods (except excluded ones)

## Useful links

- [Project on PyPI](https://pypi.org/project/digiseller-api-python/)
- [Digiseller website](https://my.digiseller.ru)
- [Digiseller API documentation](https://my.digiseller.com/inside/api.asp)
- [Hosting at great prices](https://bill.yacolo.net/billmgr?from=58735) (**Promo code:** yacolo#58735)
