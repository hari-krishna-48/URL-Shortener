"""Abstract base class for URL storage."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


class AbstractStorage(ABC):

    @abstractmethod
    def get_url(self, id: str) -> str | Optional[str]:
        """Retrieve URL by ID."""
        pass

    @abstractmethod
    def set_url(self, id: str, url: str) -> None:
        """Update URL for existing ID."""
        pass

    @abstractmethod
    def delete_id(self, id: str) -> bool:
        """Delete a ID. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def list_ids(self) -> list[str] | Optional[list[str]]:
        """List all IDs."""
        pass

    @abstractmethod
    def list_ids_by_owner(self, owner: str) -> list[str] | Optional[list[str]]:
        """List all IDs for a given owner."""
        pass

    @abstractmethod
    def delete_ids(self) -> None:
        """Delete all IDs and reset counter."""
        pass

    @abstractmethod
    def create_id(self, url: str, owner: str) -> str:
        """Create a new ID for the given URL and owner."""
        pass

    @abstractmethod
    def get_owner(self, id: str) -> str | Optional[str]:
        """Retrieve owner by ID."""
        pass
