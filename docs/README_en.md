<p align="center">
  <img src="https://i.ibb.co/hyTLSDZ/digiseller-logo.png" alt="Digiseller API Python" width="80%">
</p>

[![PyPI version](https://img.shields.io/pypi/v/digiseller-api-python.svg?cacheSeconds=3600)](https://pypi.org/project/digiseller-api-python)
[![PyPI Package Monthly Download](https://img.shields.io/pypi/dm/digiseller-api-python)](https://pypistats.org/packages/digiseller-api-python)
[![License](https://img.shields.io/github/license/Ernieleo/digiseller-api-python)](https://github.com/Ernieleo/digiseller-api-python/blob/master/LICENSE)
[![Test Status](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/test.yml/badge.svg)](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/release_pypi.yml)

Russian documentation available [here](../README.md).

**Digiseller API Python** — is an unofficial Python library for interacting with the Digiseller API.

**Important Note**: This project is not affiliated with the official Digiseller development team and is not an official library.  
Inaccuracies in some requests are possible, as comprehensive testing has not been conducted because some API methods described in the Digiseller documentation may not correspond to their description.

Full API documentation can be found on the [Digiseller website](https://my.digiseller.com/inside/api.asp).  
A list of library methods and their correspondence to the official API can be found in [MAPPING.md](MAPPING.md).   
API methods for buyers from the 'Payment' block are not available in the library.

---

## Installation

### Using PyPI:
```
sh pip install digiseller-api-python
```

### Installation from GitHub repository:
```
sh pip3 install git+https://github.com/Ernieleo/digiseller-api-python.git
```

## Usage example

To use the Digiseller API, you will need an `API Key` and a `Seller ID`:

- Get **API Key** [here](https://my.digiseller.com/inside/api_keys.asp).
- Get **Seller ID** [here](https://my.digiseller.com/).

Remember—your API key must remain secure, do not publish it on the internet.

### Code Example

```python
from digiseller_api_python import DigisellerApi

# Creating an API Client Instance
# You can specify timeout (default 60) and proxy (default None)
digiseller_api = DigisellerApi(
    seller_id="11155533", 
    api_key="ZA1SG0YDA46DV0Z39F01Z11017V39",
    timeout=120,
    proxy="http://user:pass@127.0.0.1:8080" 
)


# Example of a function for obtaining the data specified by the user when ordering by a unique code
def get_account_info_from_digiseller(unique_code):
    email, password = None, None
    try:
        # Execute the query
        data = digiseller_api.unique_code(unique_code)

        # Extract the necessary data
        for option in data.get("options", []):
            if option["name"] in ["Почта аккаунта ChatGPT", "ChatGPT account email"]:
                email = option["value"]
            elif option["name"] in ["Пароль аккаунта ChatGPT", "ChatGPT account password"]:
                password = option["value"]

        return email, password
    except Exception as e:
        # Exception handling
        print(f"Ошибка: {e}")
        return None, None


# Using the function to get information
unique_code = "YOUR_UNIQUE_CODE"
email, password = get_account_info_from_digiseller(unique_code)
print("Email:", email)
print("Password:", password)
```

This example shows how to use `DigisellerApi` to get data entered by the buyer during checkout.  
The `get_account_info_from_digiseller` function performs a request by unique code and searches for data by specified field names. Field names take into account the possibility of language differences depending on the one selected by the user on the site.

### Additional Example

To run this example, the `Pillow` library is required (`pip install Pillow`).

```python
from digiseller_api_python import DigisellerApi

from PIL import Image
from io import BytesIO

# Initialize the client (even if the method does not require authorization, the library architecture does require an instance)
# For public methods, you can pass any or empty seller_id/api_key, 
# but it's better to use the real ones to avoid confusion.
digiseller_api = DigisellerApi(seller_id="YOUR_SELLER_ID", api_key="YOUR_API_KEY")


image = digiseller_api.get_main_img(id_d=4470041, maxlength=400, w=200, h=150, crop=False)

# Opening an image from bytes directly
image_bytes = image.encode() if isinstance(image, str) else image
image = Image.open(BytesIO(image_bytes))
image.show()
```

This example presents interaction with the function for [obtaining the main product image](https://my.digiseller.com/inside/api_catgoods.asp#fast_image).

### Returned Data

- **JSON (`application/json`)**: Returned as a **Python dictionary**.
- **XML (`application/xml` or `text/xml`)**: Returned as an XML **string**.
- **Image (`image/*`)**: Returned as a **byte object**.
- **Text (`text/plain` and other text formats)**: Returned as a **string**.
- **StatusCode: 204 (NoContent)** → {"success": True}

## Exception Handling

The library provides its own exception classes, allowing you to accurately handle errors during operation.

### Base Exception

```python
from digiseller_api_python import DigisellerError
```

All library exceptions inherit from `DigisellerError`, so you can catch both specific and general errors:

```python
try:
    digiseller_api.get_token()
except DigisellerError as e:
    print(f"Ошибка Digiseller API: {e}")
```

---

### Available Exceptions

| Exception                        | Description                                                  |
|----------------------------------|--------------------------------------------------------------|
| `DigisellerError`                | Base exception                                               |
| `DigisellerTimeoutError`         | Timeout when requesting API                                  |
| `DigisellerInvalidResponseError` | API response does not match expectations (according to docs) |
| `DigisellerHTTPError`            | HTTP error (e.g., 400, 500, etc.)                            |
| `DigisellerUnavailableError`     | Digiseller is loading but not working or updating            |
| `DigisellerAPIAuthError`         | Insufficient permissions. Check access rights with API key   |
| `DigisellerProxyError`           | Error connecting via proxy                                   |
---

You can use exceptions for logging, debugging.

## Development
Contribution to the project development is welcome!  
If you want to help with maintaining relevance and further development, please follow the official rules of the Digiseller service API and adhere to the general code style of the project.

To make changes, create a fork and a subsequent pull request, and it will be reviewed.

If you find an error related to the code operation, please create an **Issue** in the repository — this will help to fix it promptly.

---

#### Appeal to Digiseller Developers.
The main request is to tidy up the documentation. In its current form, it contains many inconsistencies with the actual API operation: errors in parameter descriptions, different spellings of the same fields within one method, incomplete explanations, and clear traces of manual formatting of each page.
It's time to switch to modern standards: OpenAPI, correctly described schemas, and a convenient Swagger interface. This will significantly simplify interaction with the API and reduce the number of errors for integrators.

## Planned 
Future plans include creating documentation for convenient and correct usage.
- [x] Add all API functions
- [x] Additional usage example in Python
- [x] Add additional missing functions
- [x] Full documentation of methods (see [MAPPING.md](MAPPING.md))
- [x] Add remaining functions (with exceptions)
- [x] Add possibility to use Proxy

## Useful Links
- [Project on PyPI](https://pypi.org/project/digiseller-api-python/)
- [Digiseller Website](https://my.digiseller.ru)  
- [Digiseller API Documentation](https://my.digiseller.com/inside/api.asp)
- [Hosting with good prices](https://bill.yacolo.net/billmgr?from=58735) (**Promo code:** yacolo#58735)
