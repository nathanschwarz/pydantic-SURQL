from typing import Any, Optional, Type, Union, get_origin, get_args, get_type_hints
from types import UnionType, NoneType, GenericAlias

from pydantic import BaseModel
from .types import SurQLField, SurQLType, SurQLNullable
from datetime import datetime

def parseSimpleTypes(_type: Type):
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
    return None

def parseType(_type: Type):
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
    if (_type.__is_surql_collection__):
        test = SurQLField(name=None, types=[SurQLType.RECORD], recordLink=_type.__surql_table_name__)
        print(test)
        return test
    return parseField(name=None, annotation=_type)

def parseUnionType(type: UnionType):
    types = []
    for e in get_args(type):
        types.append(parseType(e))
    return types

def is_union(annotation: Type):
    origin = get_origin(annotation)
    return (origin == Union or origin == UnionType)

def parseFieldType(annotation: Type):
    if (is_union(annotation)):
        types = parseUnionType(annotation)
    else:
        types = [parseType(annotation)]
    return types

def parseField(name: Optional[str], annotation: Type):
    types = parseFieldType(annotation)
    #subDef = parseSubTypes(types, annotation)
    return SurQLField(name=name, types=types)

def parseFields(model: BaseModel):
    fields = []
    for field_name, field in model.model_fields.items():
        print(field_name)
        fields.append(parseField(field_name, field.annotation))
    return fields
