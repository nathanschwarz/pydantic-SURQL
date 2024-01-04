from typing import TypedDict, Type
from pydantic_surql.types import SurQLField

class Cache():
    """
        A simple cache system maping a Type to a SurQLField
    """
    def __init__(self):
        """
            Initialize the cache
        """
        self.cache: TypedDict[Type, SurQLField] = {}

    def get(self, key: str):
        """
            Get a key from the cache
        """
        return self.cache.get(key)

    def set(self, key: str, value: TypedDict):
        """
            Set a key in the cache
        """
        self.cache[key] = value

    def has(self, key: str):
        """
            Check if the cache has a key
        """
        return key in self.cache

    def clear(self):
        """
            Clear the cache
        """
        self.cache = {}