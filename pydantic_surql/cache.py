from typing import TypedDict, Type
from .types import RecursiveType, SurQLField

class Cache():
    """
        A simple cache system maping a Type to a list[RecursiveType]
    """
    def __init__(self):
        """
            Initialize the cache
        """
        self.cache: TypedDict[Type, RecursiveType | SurQLField] = {}

    def get(self, key: Type):
        """
            Get a key from the cache
        """
        return self.cache.get(key)

    def set(self, key: Type, value: TypedDict):
        """
            Set a key in the cache
        """
        self.cache[key] = value
        return value

    def has(self, key: Type):
        """
            Check if the cache has a key
        """
        return key in self.cache

    def clear(self):
        """
            Clear the cache
        """
        self.cache = {}