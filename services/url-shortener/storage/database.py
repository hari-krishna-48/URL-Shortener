"""Database(MongoDB) implementation of the storage."""

from __future__ import annotations
from threading import Lock
from typing import Optional
from utils.encoding import encode_base64
from pymongo import MongoClient, ReturnDocument
from storage.abstract_storage import AbstractStorage

from utils import config


class DatabaseStorage(AbstractStorage):

    def __init__(self) -> None:
        uri = f"mongodb://{config.mongodb_host}:{config.mongodb_port}/"
        client = MongoClient(uri)
        db = client[config.mongodb_database]
        mappings_name = config.mongodb_collections["mappings"]
        counters_name = config.mongodb_collections["counters"]
        self._mappings = db[mappings_name]   # {_id: <id>, url: <long_url>, owner: <username>}
        self._counters = db[counters_name]   # {_id: "url_id", seq: <counter>}
        self._lock = Lock()

    def get_url(self, id: str) -> str | Optional[str]:
        with self._lock:
            doc = self._mappings.find_one({"_id": id}, {"url": 1})
            return doc.get("url") if doc else None

    def get_owner(self, id: str) -> str | Optional[str]:
        with self._lock:
            doc = self._mappings.find_one({"_id": id}, {"owner": 1})
            return doc.get("owner") if doc else None

    def set_url(self, id: str, url: str) -> None:
        with self._lock:
            self._mappings.update_one(
                {"_id": id}, {"$set": {"url": url}}, upsert=False
            )

    def delete_id(self, id: str) -> bool:
        with self._lock:
            res = self._mappings.delete_one({"_id": id})
            return res.deleted_count == 1

    def list_ids(self) -> list[str] | Optional[list[str]]:
        with self._lock:
            ids = [d["_id"] for d in self._mappings.find({}, {"_id": 1})]
            return ids or None

    def list_ids_by_owner(self, owner: str) -> list[str] | Optional[list[str]]:
        with self._lock:
            ids = [d["_id"] for d in self._mappings.find({"owner": owner}, {"_id": 1})]
            return ids or None

    def delete_ids(self) -> None:
        with self._lock:
            self._mappings.delete_many({})
            self._counters.update_one(
                {"_id": "url_id"},
                {"$set": {"seq": 0}},
                upsert=True,
            )

    def create_id(self, url: str, owner: str) -> str:
        with self._lock:
            doc = self._counters.find_one_and_update(
                {"_id": "url_id"},
                {"$inc": {"seq": 1}},
                upsert=True,
                return_document=ReturnDocument.AFTER,
            )
            seq = int(doc["seq"])
            new_id = encode_base64(seq)

            # If id somehow exists, keep incrementing
            # (shouldn't happen if encoding is deterministic and counter is monotonic)
            while self._mappings.find_one({"_id": new_id}, {"_id": 1}) is not None:
                doc = self._counters.find_one_and_update(
                    {"_id": "url_id"},
                    {"$inc": {"seq": 1}},
                    upsert=True,
                    return_document=ReturnDocument.AFTER,
                )
                seq = int(doc["seq"])
                new_id = encode_base64(seq)
            self._mappings.insert_one({"_id": new_id, "url": url, "owner": owner})
            return new_id

