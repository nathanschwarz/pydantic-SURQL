from typing import TypedDict, Type
from .types import SurQLField

CacheKey = tuple[str, Type]

class Cache():
    """
        A simple cache system maping a Type to a SurQLField
    """
    def __init__(self):
        """
            Initialize the cache
        """
        self.cache: TypedDict[CacheKey, SurQLField] = {}

    def get(self, key: CacheKey):
        """
            Get a key from the cache
        """
        return self.cache.get(key)

    def set(self, key: CacheKey, value: TypedDict):
        """
            Set a key in the cache
        """
        self.cache[key] = value

    def has(self, key: CacheKey):
        """
            Check if the cache has a key
        """
        return key in self.cache

    def clear(self):
        """
            Clear the cache
        """
        self.cache = {}