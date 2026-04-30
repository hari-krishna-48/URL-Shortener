from .abstract_storage import AbstractStorage
from utils.password import hash_password, verify_password


class MemoryStorage(AbstractStorage):
    def __init__(self) -> None:
        self._users: dict[str, str] = {}

    def create_user(self, username: str, password: str) -> bool:
        if username in self._users:
            return False
        self._users[username] = hash_password(password)
        return True

    def update_password(self, username: str, old_password: str, new_password: str) -> bool:
        if username not in self._users:
            return False
        if not verify_password(old_password, self._users[username]):
            return False
        self._users[username] = hash_password(new_password)
        return True

    def verify_password(self, username: str, password: str) -> bool:
        stored = self._users.get(username)
        if stored is None:
            return False
        return verify_password(password, stored)
