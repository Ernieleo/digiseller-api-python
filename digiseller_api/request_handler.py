import httpx
import json


def send_request(method, url, **kwargs):
    if 'files' in kwargs:
        headers = {'Accept': 'application/json; charset=UTF-8'}
    else:
        headers = {'Accept': 'application/json; charset=UTF-8', 'Content-Type': 'application/json'}
    kwargs['headers'] = headers

    with httpx.Client() as client:
        response = client.request(method, url, **kwargs)

        # Check if the response contains JSON
        if response.headers.get("Content-Type") == "application/json; charset=utf-8" or response.headers.get("Content-Type") == "application/json":
            try:
                return response.json()
            except json.JSONDecodeError:
                raise ValueError(f"Error decoding JSON, response received: {response.text}")

        # If Content-Type is not JSON
        else:
            if response.text:
                # The response contains text data
                return response.text
            return response.status_code