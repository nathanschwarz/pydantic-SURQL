from typing import Any, Optional, Type, Union, get_origin, get_args
from types import UnionType, NoneType, GenericAlias
from .types import SchemaType, SurQLField, SurQLType, SurQLNullable
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
        return SurQLType.OBJECT
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
    if (_type == dict):
        return SurQLType.OBJECT
    return SurQLType.RECORD

def parseUnionType(type: UnionType):
    types = []
    for e in get_args(type):
        types.append(parseType(e))
    return types

# def parseSubType(_type: list):
#     types = []
#     for e in _type:
#         simpleType = parseSimpleTypes(e)
#         if (simpleType is not None):
#             types.append(simpleType)
#         else:
#             origin = get_origin(e)
#             if (origin == Union or origin == UnionType):
#                 for arg in get_args(e):
#                     simpleType = parseSimpleTypes(arg)
#                     if (simpleType is not None):
#                         types.append(simpleType)
#                     else:
#                         types.append(e)
#             else:
#                 types.append(e)
#     return types

# def parseSubTypes(types: list, annotation: Type):
#     subDef = []
#     for _type in types:
#         if (
#             _type == SurQLType.ARRAY or
#             _type == SurQLType.OBJECT or
#             _type == SurQLType.RECORD
#         ):
#             subDef = parseSubType(get_args(annotation))
#             for (idx, sub) in enumerate(subDef):
#                 if isinstance(sub, SurQLType) is not True:
#                     subDef[idx] = parseField(name=None, annotation=sub)
#     if (len(subDef) == 0):
#         subDef = None
#     return subDef

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

def parseFields(model: SchemaType):
    fields = []
    for field_name, field in model.model_fields.items():
        fields.append(parseField(field_name, field.annotation))
    return fields
