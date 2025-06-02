import httpx
import json
from ._exceptions import (
    DigisellerError,
    DigisellerTimeoutError,
    DigisellerInvalidResponseError,
    DigisellerHTTPError,
)


def send_request(method, url, **kwargs):

    kwargs['headers'] = {"Accept": "application/json, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.7"}

    if 'files' in kwargs:
        headers = {'Accept': 'application/json'}
        kwargs['headers'] = headers

    try:
        with httpx.Client(timeout=10) as client:
            response = client.request(method, url, **kwargs)
            if response.status_code == 200:

                content_type = response.headers.get("Content-Type", "")

                # Обработка JSON ответа
                if content_type.startswith("application/json"):
                    try:
                        return response.json()
                    except json.JSONDecodeError as e:
                        raise DigisellerInvalidResponseError(f"Json decoding error: {e}. Data: {response.text}")

                # Обработка XML
                elif content_type.startswith(("application/xml", "text/xml")):
                    return response.text

                # Обработка изображений
                elif content_type.startswith("image/"):
                    return response.content

                # Обработка текста
                elif response.text:
                    return response.text

                return response.status_code

            else:
                raise DigisellerHTTPError(response.status_code, response.text)

    except httpx.TimeoutException:
        raise DigisellerTimeoutError("The exceeded response time from Digiseller.")

    except httpx.RequestError as e:
        raise DigisellerError(f"Error when performing a request to {e.request.url}: {e}")
