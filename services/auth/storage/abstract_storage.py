from abc import ABC, abstractmethod


class AbstractStorage(ABC):
    @abstractmethod
    def create_user(self, username: str, password: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def update_password(self, username: str, old_password: str, new_password: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def verify_password(self, username: str, password: str) -> bool:
        raise NotImplementedError
