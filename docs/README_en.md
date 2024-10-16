
# Digiseller API Python

[![PyPI version](https://img.shields.io/pypi/v/digiseller-api-python.svg?cacheSeconds=3600)](https://pypi.org/project/digiseller-api-python)
[![PyPI Package Monthly Download](https://img.shields.io/pypi/dm/digiseller-api-python)](https://pypistats.org/packages/digiseller-api-python)
[![License](https://img.shields.io/github/license/Ernieleo/digiseller-api-python)](https://github.com/Ernieleo/digiseller-api-python/blob/master/LICENSE)
[![Test Status](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/test.yml/badge.svg)](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/test.yml)

Документация на русском языке доступна [здесь](./docs/README_ru.md).

**Digiseller API Python** is an unofficial Python library for interacting with the Digiseller API.

**Important Note**: This project is not affiliated with the official Digiseller development team and is not an official library.  
Some requests may contain inaccuracies, as comprehensive testing has not been conducted. Additionally, certain API methods described in the Digiseller documentation may not correspond to their actual implementation on the site.

You can find the complete API documentation on the [Digiseller website](https://my.digiseller.com/inside/api.asp).

## Installation

The package can be installed in two ways:

### Using PyPI:
```sh
pip install digiseller-api-python
```

### Installation from the GitHub repository:
```sh
pip3 install git+https://github.com/Ernieleo/digiseller-api-python.git
```

## Example Usage

To use the Digiseller API, you will need an `API key` and a `seller ID`:

- Get your **API key** [here](https://my.digiseller.com/inside/api_keys.asp).
- Get your **seller ID** [here](https://my.digiseller.com/).

### Code Example
```python
from digiseller_api import DigisellerApi

# Initializing the API client
digiseller_api = DigisellerApi(seller_id="11155533", api_key="CA1SF69A000A46D00039F01Z11017V39")

# Example function to retrieve account details provided by the user upon purchase, using a unique code
def get_account_info_from_digiseller(unique_code):
    email, password = None, None
    try:
        # Make the request
        data = digiseller_api.unique_code(unique_code)
        
        # Extract the necessary data
        for option in data.get("options", []):
            if option["name"] in ["ChatGPT account email", "ChatGPT account email"]:
                email = option["value"]
            elif option["name"] in ["ChatGPT account password", "ChatGPT account password"]:
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

### Usage Description
This example shows how to use `DigisellerApi` to retrieve data entered by the buyer when placing an order.  
The function `get_account_info_from_digiseller` makes a request with a unique code and searches for data by field names, accounting for language differences that may depend on the language selected by the user on the site.

## Development
Contributions to the project are welcome!  
If you would like to help with keeping the project up to date or developing it further, please follow the official Digiseller API guidelines and adhere to the project's code style.

To submit changes, create a pull request, and it will be reviewed.

## Useful Links
- [Digiseller Website](https://my.digiseller.ru)  
- [Digiseller API Documentation](https://my.digiseller.com/inside/api.asp)
