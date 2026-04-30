import hashlib
import hmac
import secrets

_SALT_BYTES = 16
_HASH_ITERS = 120_000
_HASH_ALG = "sha256"


def _hash_password(password: str, salt: bytes) -> str:
    digest = hashlib.pbkdf2_hmac(_HASH_ALG, password.encode("utf-8"), salt, _HASH_ITERS)
    return digest.hex()


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(_SALT_BYTES)
    hashed = _hash_password(password, salt)
    return f"{salt.hex()}${hashed}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hashed_hex = stored.split("$", 1)
    except ValueError:
        return False
    try:
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    expected = _hash_password(password, salt)
    return hmac.compare_digest(expected, hashed_hex)
