
<p align="center">
  <img src="https://i.ibb.co/hyTLSDZ/digiseller-logo.png" alt="Digiseller API Python" width="80%">
</p>

[![PyPI version](https://img.shields.io/pypi/v/digiseller-api-python.svg?cacheSeconds=3600)](https://pypi.org/project/digiseller-api-python)
[![PyPI Package Monthly Download](https://img.shields.io/pypi/dm/digiseller-api-python)](https://pypistats.org/packages/digiseller-api-python)
[![License](https://img.shields.io/github/license/Ernieleo/digiseller-api-python)](https://github.com/Ernieleo/digiseller-api-python/blob/master/LICENSE)
[![Test Status](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/test.yml/badge.svg)](https://github.com/Ernieleo/digiseller-api-python/actions/workflows/test.yml)

Документация на русском доступна [здесь](https://github.com/Ernieleo/digiseller-api-python/blob/master/docs/README_ru.md).

**Digiseller API Python** is an unofficial Python library for interacting with the Digiseller API.

**Important Note**: This project is not affiliated with the official Digiseller development team and is not an official library.  
Some requests might be inaccurate, as comprehensive testing was not conducted. Some API methods described in the Digiseller documentation may not match their description.

The full API documentation can be found on the [Digiseller website](https://my.digiseller.com/inside/api.asp).  
API methods from the "Payment" block are not available in the library.

## Installation

### Using PyPI:
```sh
pip install digiseller-api-python
```

### Installing from GitHub repository:
```sh
pip3 install git+https://github.com/Ernieleo/digiseller-api-python.git
```

## Usage Example

To use the Digiseller API, you will need an `API key` and `Seller ID`:

- Get your **API key** [here](https://my.digiseller.com/inside/api_keys.asp).
- Get your **Seller ID** [here](https://my.digiseller.com/).

### Example Code
```python
from digiseller_api import DigisellerApi

# Creating an instance of the API client
digiseller_api = DigisellerApi(seller_id="11155533", api_key="CA1SF69A000A46D00039F01Z11017V39")

# Example function to retrieve customer-provided data by unique code
def get_account_info_from_digiseller(unique_code):
    email, password = None, None
    try:
        # Sending the request
        data = digiseller_api.unique_code(unique_code)
        
        # Extracting the necessary data
        for option in data.get("options", []):
            if option["name"] in ["ChatGPT account email", "ChatGPT account password"]:
                email = option["value"]
            elif option["name"] in ["ChatGPT account email", "ChatGPT account password"]:
                password = option["value"]
    
        return email, password
    except Exception as e:
        # Handling exceptions
        print(f"Error: {e}")
        return None, None

# Using the function to get information
unique_code = "YOUR_UNIQUE_CODE"
email, password = get_account_info_from_digiseller(unique_code)
print("Email:", email)
print("Password:", password)
```

This example demonstrates how to use `DigisellerApi` to retrieve customer-provided data during order placement.  
The `get_account_info_from_digiseller` function sends a request using the unique code and searches for data by predefined field names. These field names account for potential differences in the user's chosen language on the website.

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

This example demonstrates interaction with the [function for retrieving the main product image](https://my.digiseller.com/inside/api_catgoods.asp#fast_image). The call is made without using seller data or creating an API client instance.

### Return Data

- **JSON (`application/json`)**: Returns a **Python dictionary**.
- **XML (`application/xml` or `text/xml`)**: Returns the **XML string**.
- **Image (`image/*`)**: Returns a **byte object**.
- **Text (`text/plain` and other text formats)**: Returns a **string**.
- **Other types**: Returns the **response status code**.
- **Error**: If a problem occurs, a `ValueError` exception will be raised.

## Development
Contributions to the project are welcome!  
If you want to help maintain and develop the library further, please follow the official rules of the Digiseller API service and adhere to the general code style of the project.

To make changes, create a pull request, and it will be reviewed.

## Roadmap 
Planned improvements include creating documentation for convenient and correct usage.
- [x] Add all API functions
- [x] Additional usage example in Python
- [x] Add missing functions
- [ ] Full documentation of methods (in progress)
- [ ] Include remaining functions (by request)

## Useful Links
- [Project on PyPI](https://pypi.org/project/digiseller-api-python/)
- [Digiseller Website](https://my.digiseller.ru)  
- [Digiseller API Documentation](https://my.digiseller.com/inside/api.asp)
