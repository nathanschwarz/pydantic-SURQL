from typing import List, Type, Set, get_args
from enum import Enum
from types import UnionType, NoneType, GenericAlias
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

SchemaType = Type[BaseModel]
SurQLNullable = Type[None]

class SurQLType(Enum):
    STRING = "string"
    NUMBER = "number"
    DATE = "datetime"
    BOOLEAN = "bool"
    ARRAY = "array"
    OBJECT = "object"
    RECORD = "record"
    OPTIONAL = "optional"
    NULL = "null"

def parseType(_type: Type):
    if (_type == str):
        return SurQLType.STRING
    if (_type == int or _type == float):
        return SurQLType.NUMBER
    if (_type == datetime.date or _type == datetime):
        return SurQLType.DATE
    if (_type == bool):
        return SurQLType.BOOLEAN
    if (isinstance(_type, GenericAlias) and _type.__origin__ == list):
        return SurQLType.ARRAY
    if (_type == dict):
        return SurQLType.OBJECT
    if (_type == SurQLNullable):
        return SurQLType.OPTIONAL
    if (_type == NoneType):
        return SurQLType.NULL
    return SurQLType.RECORD

def parseUnionType(type: UnionType):
    types = []
    for e in get_args(type):
        types.append(parseType(e))
    if (len(types) == 0):
       return None
    return types

def parseSubType(_type: list):
    types = []
    if (len(_type) == 0):
        return None
    for e in _type:
        if (e == str):
            types.append(SurQLType.STRING)
        elif (e == int or e == float):
            types.append(SurQLType.NUMBER)
        elif (e == datetime.date or e == datetime):
            types.append(SurQLType.DATE)
        elif (e == bool):
            types.append(SurQLType.BOOLEAN)
        else:
            types.append(e)
    return types

class SurQLField(BaseModel):
    name: Optional[str]
    types: list[SurQLType]
    subDef: Optional[list[SurQLType] | SurQLType | SchemaType | 'SurQLField']

SurQLField.model_rebuild()

class SurQLSchema(BaseModel):
    name: str
    fields: list[SurQLField]


class SurQLTable(SurQLSchema):
    name: str
    fields: Set[SurQLField]

class SurQLMapper(BaseModel):
    tables: Set[SurQLTable]