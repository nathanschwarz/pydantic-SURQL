from typing import Type, Union, get_origin, get_args
from types import UnionType, NoneType, GenericAlias
from .types import SchemaType, SurQLField, SurQLType, SurQLNullable
from datetime import datetime
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

def parseFields(model: SchemaType):
    print(model)
    fields = []
    for field_name, field in model.model_fields.items():
        types = []
        subDef = None
        origin = get_origin(field.annotation)
        if (origin == Union):
            types = parseUnionType(field.annotation)
        else:
            types = [parseType(field.annotation)]
        for _type in types:
            if (
                _type == SurQLType.ARRAY or
                _type == SurQLType.OBJECT or
                _type == SurQLType.RECORD
            ):
                subDef = parseSubType(get_args(field.annotation))
                if isinstance(subDef, SurQLType) is not True:
                    print(subDef, field.annotation)
        fields.append(SurQLField(name=field_name, types=types, subDef=subDef))
    return fields
