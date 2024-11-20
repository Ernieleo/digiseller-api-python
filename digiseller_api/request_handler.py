import httpx
import json


def send_request(method, url, **kwargs):
    if 'files' in kwargs:
        headers = {'Accept': 'application/json; charset=UTF-8'}
        kwargs['headers'] = headers

    with httpx.Client(timeout=10) as client:
        response = client.request(method, url, **kwargs)
        # response.raise_for_status()

        if response.status_code <= 200:

            content_type = response.headers.get("Content-Type", "")

            # Обработка JSON ответа
            if content_type.startswith("application/json"):
                try:
                    return response.json()
                except json.JSONDecodeError:
                    raise ValueError(f"Error decoding JSON, response received: {response.text}")

            # Обработка XML ответа (оставляю как есть)
            elif content_type.startswith("application/xml") or content_type.startswith("text/xml"):
                return response.text

            # Обработка изображений
            elif content_type.startswith("image/"):
                return response.content

            # Обработка текста
            elif response.text:
                return response.text

            return response.status_code

        else:
            raise ValueError(f"Response with a bad http code was received: {response.status_code} / {response.text}")