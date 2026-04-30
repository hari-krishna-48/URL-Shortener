import os
from typing import Any

import requests

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://127.0.0.1:8001')
VERIFY_ENDPOINT = '/auth/verify'


def verify_jwt(token: str) -> dict[str, Any] | None:
    if not token:
        return None

    if token.lower().startswith('bearer '):
        token = token[7:].strip()

    try:
        response = requests.post(
            f"{AUTH_SERVICE_URL}{VERIFY_ENDPOINT}",
            json={'token': token},
            timeout=2,
        )
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:
        payload = response.json().get('payload')
    except ValueError:
        return None

    if not isinstance(payload, dict):
        return None

    return payload
