
# Digiseller API Python

[![PyPI version](https://img.shields.io/pypi/v/digiseller-api-python.svg?cacheSeconds=3600)](https://pypi.org/project/digiseller-api-python)
[![PyPI Package Monthly Download](https://img.shields.io/pypi/dm/digiseller-api-python)](https://pypistats.org/packages/digiseller-api-python)
[![License](https://img.shields.io/github/license/Ernieleo/digiseller-api-python)](https://github.com/Ernieleo/digiseller-api-python/blob/master/LICENSE)
[![Test Status](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/test.yml/badge.svg)](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/test.yml)

Документация на русском доступна [здесь](https://github.com/Ernieleo/digiseller-api-python/blob/master/docs/README_ru.md).

**Digiseller API Python** is an unofficial Python library for interacting with the Digiseller API.

**Important Note**: This project is not affiliated with the official Digiseller development team and is not an official library.  
Some requests may contain inaccuracies, as comprehensive testing has not been conducted. Also, certain API methods described in the Digiseller documentation may not match their descriptions on the website.

You can find the full API documentation on the [Digiseller website](https://my.digiseller.com/inside/api.asp).

## Installation

### Using PyPI:
```sh
pip install digiseller-api-python
```

### Installation from the GitHub repository:
```sh
pip3 install git+https://github.com/Ernieleo/digiseller-api-python.git
```

## Example Usage

To use the Digiseller API, you will need your `API key` and `Seller ID`:

- Get your **API key** [here](https://my.digiseller.com/inside/api_keys.asp).
- Find your **Seller ID** [here](https://my.digiseller.com/).

### Code Example
```python
from digiseller_api import DigisellerApi

# Initializing the API client
digiseller_api = DigisellerApi(seller_id="11155533", api_key="CA1SF69A000A46D00039F01Z11017V39")

# Example function to retrieve account details provided by the user upon purchase, using a unique code
def get_account_info_from_digiseller(unique_code):
    email, password = None, None
    try:
        # Execute request
        data = digiseller_api.unique_code(unique_code)
        
        # Extract necessary data
        for option in data.get("options", []):
            if option["name"] in ["ChatGPT account email"]:
                email = option["value"]
            elif option["name"] in ["ChatGPT account password"]:
                password = option["value"]
    
        return email, password
    except Exception as e:
        # Exception handling
        print(f"Error: {e}")
        return None, None

# Using the function to retrieve information
unique_code = "YOUR_UNIQUE_CODE"
email, password = get_account_info_from_digiseller(unique_code)
print("Email:", email)
print("Password:", password)
```

This example shows how to use `DigisellerApi` to retrieve data entered by the buyer during order placement.  
The function `get_account_info_from_digiseller` executes a request using a unique code and searches for data by field names, accounting for language differences depending on the user's language selection on the site.

### Additional Example
```python
from digiseller_api import DigisellerApi

from PIL import Image
from io import BytesIO

image = DigisellerApi.get_main_img(id_d=4470041, maxlength=400)
# Open the image directly from bytes
image_bytes = image.encode() if isinstance(image, str) else image
image = Image.open(BytesIO(image_bytes))
image.show()
```

This example demonstrates interaction with the function for [fetching a product's main image](https://my.digiseller.com/inside/api_catgoods.asp#fast_image), allowing access without the need set seller ID and API client instance creation.

## Development
Contributions to the project are welcome!  
If you'd like to help keep the project up-to-date or develop it further, please follow the official Digiseller API rules and adhere to the project’s code style.

To submit changes, create a pull request, and it will be reviewed.

## Future Plans 
Documentation for all methods will be created for convenient and accurate use.
- [x] Added all API functions
- [x] Additional usage example in Python
- [ ] Full method documentation (in progress)
- [ ] Additional features (planned)

## Useful Links
- [Project on PyPI](https://pypi.org/project/digiseller-api-python/)
- [Digiseller Website](https://my.digiseller.ru)  
- [Digiseller API Documentation](https://my.digiseller.com/inside/api.asp)