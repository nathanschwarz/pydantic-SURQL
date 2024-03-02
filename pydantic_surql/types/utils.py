from ctypes import Union
from enum import Enum
from types import UnionType
from typing import Type, get_origin

SurQLNullable = Type[None]
"""
    A custom type to define a nullable field
"""

SurQLAnyRecord = Type[dict]
"""
    A custom type to define a generic record
"""

class SurQLType(Enum):
    """
        SurQL types enumeration
    """
    STRING = "string"
    NUMBER = "number"
    DATE = "datetime"
    ANY = "any"
    BOOLEAN = "bool"
    ENUM = "enum"
    ARRAY = "array"
    OBJECT = "object"
    SET = "set"
    RECORD = "record<%s>"
    ANY_RECORD = "record()"
    OPTIONAL = "option<%s>"
    NULL = "null"

def is_union(annotation: Type) -> bool:
    """
        Check if a type is a Union
    """
    origin = get_origin(annotation)
    return (origin == Union or origin == UnionType)
