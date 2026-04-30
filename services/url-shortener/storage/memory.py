"""In-memory implementation of the storage."""

from __future__ import annotations
from threading import Lock
from typing import Optional
from utils.encoding import encode_base64
from storage.abstract_storage import AbstractStorage


class MemoryStorage(AbstractStorage):

    def __init__(self) -> None:
        self._storage: dict[str, dict[str, str]] = {}
        self._counter: int = 0
        self._lock = Lock()

    def get_url(self, id: str) -> str | Optional[str]:
        with self._lock:
            data = self._storage.get(id)
            return data.get("url") if data else None

    def get_owner(self, id: str) -> str | Optional[str]:
        with self._lock:
            data = self._storage.get(id)
            return data.get("owner") if data else None

    def set_url(self, id: str, url: str) -> None:
        with self._lock:
            if id in self._storage:
                self._storage[id]["url"] = url

    def delete_id(self, id: str) -> bool:
        with self._lock:
            if id in self._storage:
                del self._storage[id]
                return True
            return False

    def list_ids(self) -> list[str] | Optional[list[str]]:
        with self._lock:
            return list(self._storage.keys()) or None

    def list_ids_by_owner(self, owner: str) -> list[str] | Optional[list[str]]:
        with self._lock:
            ids = [id for id, data in self._storage.items() if data.get("owner") == owner]
            return ids or None

    def delete_ids(self) -> None:
        with self._lock:
            self._counter = 0
            self._storage.clear()

    def create_id(self, url: str, owner: str) -> str:
        with self._lock:
            self._counter += 1
            new_id = encode_base64(self._counter)
            while new_id in self._storage:
                self._counter += 1
                new_id = encode_base64(self._counter)
            self._storage[new_id] = {"url": url, "owner": owner}
            return new_id
