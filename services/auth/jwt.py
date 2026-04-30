import base64
import hashlib
import hmac
import json
import os
import time
from pathlib import Path

_CONFIG_PATH = Path(__file__).resolve().parent / 'config.json'
with open(_CONFIG_PATH, encoding='utf-8') as f:
    _config = json.load(f)

JWT_SECRET = os.getenv('AUTH_JWT_SECRET', _config['jwt']['secret'])
JWT_TTL_SECONDS = int(_config['jwt'].get('ttl_seconds', 3600))
JWT_ALG = 'HS256'


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')


def _sign_hs256(message: bytes, secret: str) -> str:
    digest = hmac.new(secret.encode('utf-8'), message, hashlib.sha256).digest()
    return _b64url_encode(digest)


def _b64url_decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def generate_jwt(username: str, ttl_seconds: int | None = None) -> str:
    header = {'alg': JWT_ALG, 'typ': 'JWT'}
    now = int(time.time())
    ttl = JWT_TTL_SECONDS if ttl_seconds is None else int(ttl_seconds)
    payload = {
        'username': username,
        'iat': now,
        'exp': now + ttl,
    }

    header_b64 = _b64url_encode(json.dumps(header, separators=(',', ':'), sort_keys=True).encode('utf-8'))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(',', ':'), sort_keys=True).encode('utf-8'))
    signing_input = f"{header_b64}.{payload_b64}".encode('ascii')
    signature_b64 = _sign_hs256(signing_input, JWT_SECRET)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def verify_jwt(token: str) -> dict | None:
    if not token:
        return None

    if token.lower().startswith('bearer '):
        token = token[7:].strip()

    parts = token.split('.')
    if len(parts) != 3:
        return None

    header_b64, payload_b64, signature_b64 = parts
    try:
        header = json.loads(_b64url_decode(header_b64))
        payload = json.loads(_b64url_decode(payload_b64))
    except (json.JSONDecodeError, ValueError):
        return None

    if header.get('alg') != JWT_ALG or header.get('typ') != 'JWT':
        return None

    signing_input = f"{header_b64}.{payload_b64}".encode('ascii')
    expected_sig = _sign_hs256(signing_input, JWT_SECRET)
    if not hmac.compare_digest(expected_sig, signature_b64):
        return None

    exp = payload.get('exp')
    if isinstance(exp, int) and exp < int(time.time()):
        return None

    return payload
