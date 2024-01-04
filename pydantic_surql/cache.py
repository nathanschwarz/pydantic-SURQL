from typing import TypedDict, Type
from pydantic_surql.types import SurQLField

class Cache():
    def __init__(self):
        self.cache: TypedDict[Type, SurQLField] = {}

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value: TypedDict):
        self.cache[key] = value

    def has(self, key: str):
        return key in self.cache

    def clear(self):
        self.cache = {}