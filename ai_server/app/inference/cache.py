"""
Simple in-memory LRU cache for responses.
"""
from collections import OrderedDict
from typing import Any, Optional


class LRUCache:
    def __init__(self, max_items: int = 128) -> None:
        self.max_items = max_items
        self._store: "OrderedDict[str, Any]" = OrderedDict()

    def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        self._store.move_to_end(key)
        return self._store[key]

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value
        self._store.move_to_end(key)
        if len(self._store) > self.max_items:
            self._store.popitem(last=False)
