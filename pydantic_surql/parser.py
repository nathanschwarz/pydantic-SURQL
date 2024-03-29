from enum import Enum
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional, Type, Union, get_origin, get_args
from types import UnionType, NoneType, GenericAlias

from pydantic_surql.types.field import SurQLFieldInfo

from .cache import Cache
from .types import RecursiveType, SurQLAnyRecord, SurQLField, SurQLType, SurQLNullable, SurQLTable, SurQLTableConfig

def is_union(annotation: Type) -> bool:
    """
        Check if a type is a Union
    """
    origin = get_origin(annotation)
    return (origin == Union or origin == UnionType)

class SurQLParser:
    """
        A pydantic SurQL parser
    """
    def __init__(self):
        self.cache = Cache()

    @staticmethod
    def to_simple_type(_type: Type) -> SurQLType | None:
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
        if (_type == SurQLNullable):
            return SurQLType.NULL
        if (_type == NoneType):
            return SurQLType.OPTIONAL
        if (_type == SurQLAnyRecord):
            return SurQLType.ANY_RECORD
        return None

    def from_type(self, _type: Type) -> RecursiveType | SurQLField:
        """
            Parse a type:
            TODO: check for objects recursive types (will raise: must be converted to record)
        """
        if (self.cache.has(_type)):
            return self.cache.get(_type)

        # is a simple type
        simpleType = self.to_simple_type(_type)
        if (simpleType is not None):
            return self.cache.set(_type, simpleType)

        # is a list
        if (isinstance(_type, GenericAlias) and _type.__origin__ == list):
            args = get_args(_type)
            res = []
            for arg in args:
                simpleType = self.to_simple_type(arg)
                if (simpleType is not None):
                    res.append(simpleType)
                elif (is_union(arg)):
                    res += self.from_union(arg)
                else:
                    res.append(self.from_type(arg))
            return self.cache.set(_type, res)

        # is a set
        if (isinstance(_type, GenericAlias) and _type.__origin__ == set):
            args = get_args(_type)
            res = []
            for arg in args:
                simpleType = self.to_simple_type(arg)
                if (simpleType is not None):
                    res.append(simpleType)
                elif (is_union(arg)):
                    res += self.from_union(arg)
                else:
                    res.append(self.from_type(arg))
            return self.cache.set(_type, [SurQLType.SET, res])

        # is an enum
        if issubclass(_type, Enum):
            assertions = ",".join([f'"{item.value}"' if isinstance(item.value, str) else str(item.value) for item in _type])
            return SurQLField(name=None, types=[SurQLType.ENUM], assertion=f"$value in [{assertions}]")
        # is a pydantic model
        if (issubclass(_type, BaseModel)):
            if hasattr(_type, '__is_surql_collection__'):
                # was decorated with @surql_collection
                return SurQLField(name=None, types=[SurQLType.RECORD], recordLink=_type.__surql_table_name__)
            extra = _type.model_config.get('extra')
            if extra == 'allow':
                return SurQLField(name=None, types=self.from_fields(_type), recordLink=None, isFlexible=True)
            return SurQLField(name=None, types=self.from_fields(_type), recordLink=None)
        raise Exception(f"Type {_type} is not supported")

    def from_union(self, type: UnionType) -> RecursiveType:
        """
            Parse a Union type
        """
        types = []
        if (self.cache.has(type)):
            types = self.cache.get(type)
        else:
            for e in get_args(type):
                types.append(self.from_type(e))
        return self.cache.set(type, types)

    def from_field_type(self, annotation: Type) -> RecursiveType:
        """
            Parse a pydantic model field type to a SurQLField
        """
        if (is_union(annotation)):
            types = self.from_union(annotation)
        else:
            types = [self.from_type(annotation)]
        return types

    def from_field(self, name: Optional[str], annotation: Type) -> SurQLField:
        """
            Parse a pydantic model field to a SurQLField
        """
        types = self.from_field_type(annotation)
        return SurQLField(name=name, types=types)

    def from_fields(self, model: BaseModel) -> list[SurQLField]:
        """
            Parse a pydantic model to a list of SurQLField
        """
        fields = []
        for field_name, field in model.model_fields.items():
            perms = None
            if isinstance(field, SurQLFieldInfo):
                perms = field.perms
            is_collection = getattr(model, '__is_surql_collection__', False)
            if (field_name != 'id' or is_collection == False):
                _field = None
                _field = self.from_field(field_name, field.annotation)
                _field.perms = perms
                fields.append(_field)
        return fields

    def from_model(self, name: str, model: BaseModel, config: SurQLTableConfig = SurQLTableConfig()) -> SurQLTable:
        """
            Convert a pydantic model to a SurQLTable
            can be used at runtime
        """
        model.__is_surql_collection__ = True
        model.__surql_table_name__ = name
        extra = model.model_config.get('extra')
        if extra == 'allow':
            config.strict = False
        elif config.strict == False:
            model.model_config['extra'] = 'allow'
        return SurQLTable(name=name, fields=self.from_fields(model), config=config)