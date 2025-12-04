import httpx
import json
from ._exceptions import (
    DigisellerError,
    DigisellerTimeoutError,
    DigisellerInvalidResponseError,
    DigisellerHTTPError,
    DigisellerUnavailableError,
    DigisellerAPIAuthError
)


def send_request(method, url: str, timeout: int = 60, proxy: str = None, **kwargs):

    default_headers = {"Accept": "application/json, application/xml;q=0.9, text/xml;q=0.8, */*;q=0.7"}

    if 'files' in kwargs:
        default_headers = {'Accept': 'application/json'}

    # Инициализируем заголовки, если их нет, или дополняем существующие
    if 'headers' not in kwargs:
        kwargs['headers'] = default_headers
    else:
        for key, value in default_headers.items():
            kwargs['headers'].setdefault(key, value)

    try:
        with httpx.Client(timeout=timeout, proxy=proxy) as client:
            #print(f'Sending request to {url}...')
            response = client.request(method, url, **kwargs)
            content_type = response.headers.get("Content-Type", "")

            if response.status_code in (401, 403):
                raise DigisellerAPIAuthError(
                    "Access denied. Check your API key access permissions and try again..")

            elif response.status_code in (200, 400):
                #print(f"Received a {response.status_code} response from Digiseller. {response.url}")

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

                # HTML ловим
                elif content_type.startswith("text/html"):
                    raise DigisellerInvalidResponseError(
                        f"Received unexpected HTML content. "
                        f"Check the URL and parameters. Preview:\n{response.text[:300]}"
                    )

                # Всё остальное
                elif response.text:
                    return response.text

                else:
                    return response.status_code

            elif response.status_code == 204:
                return {"success": True}

            else:
                # Сервер вернул HTML
                if content_type.startswith("text/html"):
                    text = response.text.strip()

                    if any(keyword in text for keyword in ("Digiseller UPDATING", "404 - File or directory not found", "Server Error", "Digiseller is experiencing an unscheduled maintenance work")):
                        raise DigisellerUnavailableError(
                            f"Digiseller is likely undergoing maintenance.\n"
                            f"Response code: {response.status_code}\n"
                            f"URL: {response.url}\n"
                            f"Preview:\n{text[:300]}"
                        )
                    else:
                        raise DigisellerInvalidResponseError(
                            f"An unexpected HTML response was received. Perhaps the path or parameters are incorrect.\n"
                            f"Response code: {response.status_code}\n"
                            f"URL: {response.url}\n"
                            f"Preview:\n{text[:300]}"
                        )

                # Если не HTML
                raise DigisellerHTTPError(response.status_code, response.text)

    except httpx.TimeoutException:
        raise DigisellerTimeoutError("The exceeded response time from Digiseller.")

    except httpx.RequestError as e:
        raise DigisellerError(f"Error when performing a request to {e.request.url}: {e}")