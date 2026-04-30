from .memory import MemoryStorage
from .database import DatabaseStorage
from storage.abstract_storage import AbstractStorage
from utils import config


def get_storage() -> AbstractStorage:
    if config.bonus:
        from storage.database import DatabaseStorage
        return DatabaseStorage()
    return MemoryStorage()


_storage = get_storage()


def create_user(username: str, password: str) -> bool:
    return _storage.create_user(username, password)


def update_password(username: str, old_password: str, new_password: str) -> bool:
    return _storage.update_password(username, old_password, new_password)


def verify_password(username: str, password: str) -> bool:
    return _storage.verify_password(username, password)
