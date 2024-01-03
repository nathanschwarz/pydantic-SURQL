from pydantic import BaseModel
from typing import Type, Union, get_origin, get_args
from types import UnionType, NoneType
from datetime import datetime
from .types import SurQLSchema, SchemaType, SurQLField, SurQLType, SurQLTable, SurQLMapper, SurQLNullable, parseType, parseUnionType, parseSubType

Mapper = SurQLMapper(tables=[])

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
    print(fields)
    return fields

def toSurql(name: str):
    """
    Convert a pydantic model to a surQL query
    """
    def inner(model: SchemaType):
        table = SurQLTable(name=name, fields=[])
        fields = parseFields(model)

            #print(types, subDef)
                #table.fields.append(field)
            # if field_type == str:
            #     field_type = SurQLType.STRING
            # elif field_type == int or field_type == float:
            #     field_type = SurQLType.NUMBER
            # elif field_type == bool:
            #     field_type = SurQLType.BOOLEAN
            # elif field_type == list:
            #     field_type = SurQLType.ARRAY
            # elif field_type == dict:
            #     field_type = SurQLType.OBJECT
            # else:
            #     field_type = SurQLType.RECORD
            # field = SurQLField(name=field_name, types=[field_type], subDef=None, optional=field.required)
            # table.fields.append(field)
        #print(model.model_fields)
    return inner