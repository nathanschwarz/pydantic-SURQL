from typing import Any, Optional, Type, Union, get_origin, get_args
from types import UnionType, NoneType, GenericAlias
from .cache import Cache

from pydantic import BaseModel
from .types import RecursiveType, SurQLAnyRecord, SurQLField, SurQLType, SurQLNullable
from datetime import datetime

cache = Cache()

def parseSimpleTypes(_type: Type) -> SurQLType | None:
    """
        Parse simple type definitions
    """
    if (_type == str):
        return SurQLType.STRING
    if (_type == int or _type == float):
        return SurQLType.NUMBER
    if (_type == datetime.date or _type == datetime):
        return SurQLType.DATE
    if (_type == bool):
        return SurQLType.BOOLEAN
    if (_type == Any):
        return SurQLType.ANY
    if (_type == dict):
        return SurQLType.DICT
    if (_type == SurQLNullable):
        return SurQLType.NULL
    if (_type == NoneType):
        return SurQLType.OPTIONAL
    if (_type == SurQLAnyRecord):
        return SurQLType.ANY_RECORD
    return None

def parseType(_type: Type) -> RecursiveType:
    """
        Parse a type:
        TODO: check for objects recursive types (will raise: must be converted to record)
    """
    simpleType = parseSimpleTypes(_type)
    if (simpleType is not None):
        return simpleType
    if (isinstance(_type, GenericAlias) and _type.__origin__ == list):
        args = get_args(_type)
        res = []
        for arg in args:
            simpleType = parseSimpleTypes(arg)
            if (simpleType is not None):
                res.append(simpleType)
            elif (is_union(arg)):
                res += parseUnionType(arg)
            else:
                res.append(parseType(arg))
        return res
    if hasattr(_type, '__is_surql_collection__'):
        return SurQLField(name=None, types=[SurQLType.RECORD], recordLink=_type.__surql_table_name__)
    return SurQLField(name=None, types=parseFields(_type), recordLink=None)

def parseUnionType(type: UnionType) -> RecursiveType:
    """
        Parse a Union type
    """
    types = []
    for e in get_args(type):
        types.append(parseType(e))
    return types

def is_union(annotation: Type) -> bool:
    """
        Check if a type is a Union
    """
    origin = get_origin(annotation)
    return (origin == Union or origin == UnionType)

def parseFieldType(annotation: Type) -> RecursiveType:
    """
        Parse a pydantic model field type to a SurQLField
    """
    if (is_union(annotation)):
        types = parseUnionType(annotation)
    else:
        types = [parseType(annotation)]
    return types

def parseField(name: Optional[str], annotation: Type):
    """
        Parse a pydantic model field to a SurQLField
    """
    types = parseFieldType(annotation)
    #subDef = parseSubTypes(types, annotation)
    return SurQLField(name=name, types=types)

def parseFields(model: BaseModel) -> list[SurQLField]:
    """
        Parse a pydantic model to a list of SurQLField
    """
    fields = []
    for field_name, field in model.model_fields.items():
        _field = None
        if (cache.has(field.annotation)):
            _field = cache.get(field.annotation)
        else:
            _field = parseField(field_name, field.annotation)
            cache.set(field.annotation, _field)
        fields.append(_field)
    return fields
