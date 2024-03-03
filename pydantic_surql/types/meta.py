from __future__ import annotations
from datetime import datetime
from enum import Enum
from types import GenericAlias, NoneType
from typing import Any, Optional, Type, get_args
from pydantic import BaseModel, Field, field_serializer
from pydantic_surql.cache import Cache
from pydantic_surql.types.config import SurQLTableConfig

from pydantic_surql.types.utils import SurQLAnyRecord, SurQLNullable, is_union
from pydantic_surql.types.field import SurQLFieldInfo, SurQLType
from pydantic_surql.types.permissions import SurQLPermissions

class BaseType(BaseModel):
    __is_surql_collection__: bool
    __surql_table_name__: str
    __surql_schema__: Schema
    __surql_config__: SurQLTableConfig

class Schema(BaseModel):
    """
        A simple schema definition
    """
    fields: list[SchemaField]

    @staticmethod
    def from_pydantic_model(model: BaseType, name: str, cache: Cache) -> Schema:
        """
            Create a schema from a pydantic model
        """
        if (cache.has(model)):
            return cache.get(model)
        fields = []
        for field_name, field in model.model_fields.items():
            fieldName = name + '.' + field_name if name is not None else field_name
            _field = SchemaField.from_type(fieldName, field.annotation, cache)
            fields.append(_field)
        schema = Schema(fields=fields)
        cache.set(model, schema)
        return schema

    @property
    def sdl(self) -> str:
        """
            Get the SDL representation of the schema
        """
        return "\n".join([field.sdl for field in self.fields])


class MetaType(BaseModel):
    type: SurQLType
    original: Type
    subType: Type | None = None

    @field_serializer('original', 'subType')
    def serialize_orignal(self, value: Type | None) -> str | None:
        """
            Serialize the original type
        """
        if (value is None):
            return None
        return value.__name__

    @property
    def flexible(self) -> bool:
        """
            Check if the field is flexible
        """
        return self.type is SurQLType.OBJECT and self.original.model_config.get('extra') == 'allow'

    @property
    def recordLink(self) -> str | None:
        """
            Get the record link
        """
        return self.original.__surql_table_name__ if self.type is SurQLType.RECORD else None

    @property
    def perms(self) -> Optional[SurQLPermissions]:
        """
            Get the permissions
        """
        return self.original.perms if isinstance(self.original, SurQLFieldInfo) else None

    @property
    def assertions(self) -> Optional[str]:
        """
            Get the assertion
        """
        if (self.type == SurQLType.ENUM):
            __assertions = ",".join([f'"{item.value}"' if isinstance(item.value, str) else str(item.value) for item in self.original])
            return f"$value in [{__assertions}]"
        return None

    @property
    def hasDefinition(self) -> bool:
        """
            Check if the field has sub definitions
        """
        if (self.type == SurQLType.OBJECT):
            _original: BaseModel = self.original
            return len(_original.model_fields) > 0
        return self.type in [SurQLType.ARRAY, SurQLType.SET]

    @staticmethod
    def __get_type(type: Type) -> SurQLType:
        """
            Get the type from a pydantic field
        """
        if (isinstance(type, GenericAlias) and type.__origin__ == list):
            return SurQLType.ARRAY
        if (isinstance(type, GenericAlias) and type.__origin__ == set):
            return SurQLType.SET
        if (type == str):
            return SurQLType.STRING
        if (type == int or type == float):
            return SurQLType.NUMBER
        if (type == datetime):
            return SurQLType.DATE
        if (type == bool):
            return SurQLType.BOOLEAN
        if (type == Any):
            return SurQLType.ANY
        if (type == SurQLNullable):
            return SurQLType.NULL
        if (type == NoneType):
            return SurQLType.OPTIONAL
        if (type == SurQLAnyRecord):
            return SurQLType.ANY_RECORD
        if issubclass(type, Enum):
            return SurQLType.ENUM
        if issubclass(type, BaseType):
            return SurQLType.RECORD
        if (issubclass(type, BaseModel)):
            return SurQLType.OBJECT
        raise ValueError(f"Type {type} is not supported")

    @staticmethod
    def from_type(originalType: Type) -> MetaType:
        """
            Create a schema field meta from a type
        """
        _type = MetaType.__get_type(originalType)
        _original = originalType
        subType = None
        if (_type == SurQLType.ARRAY):
            _original = list
            subType = get_args(originalType)[0]
        elif (_type == SurQLType.SET):
            _original = set
            subType = get_args(originalType)[0]
        return MetaType(
            type=_type,
            original=_original,
            subType=subType
        )

class SchemaField(BaseModel):
    """
        A simple schema field definition
    """
    name: str
    metas: list[MetaType] = Field(min_length=1)
    definitions: list[Schema | SchemaField] = []

    @staticmethod
    def from_type(name: str, type: Type, cache: Cache) -> SchemaField:
        """
            Create a schema field from a type
        """
        metas: list[MetaType] = []
        definitions = []
        if (is_union(type)):
            types = get_args(type)
            metas = [MetaType.from_type(t) for t in types]
        else:
            metas = [MetaType.from_type(type)]
        for meta in metas:
            if (meta.hasDefinition):
                if (meta.type == SurQLType.OBJECT):
                    definitions.append(Schema.from_pydantic_model(type, name, cache))
                else:
                    # is a list or set
                    definitions.append(SchemaField.from_type(f"{name}.*", meta.subType, cache))
        return SchemaField(name=name, metas=metas, definitions=definitions)

    @property
    def sdl(self) -> str:
        """
            Get the SDL representation of the schema field
        """
        _split = self.name.split('.')
        table_name = _split[0]
        field_path = ".".join(_split[1:])
        tokens: list[str] = [f"DEFINE FIELD {field_path} ON TABLE {table_name}"]
        isFlexible = any([m.flexible for m in self.metas])
        tokens.append("FLEXIBLE TYPE" if isFlexible else "TYPE")
        isOptional = False
        types: list[str] = []
        for meta in self.metas:
            if (meta.type == SurQLType.OPTIONAL):
                isOptional = True
            elif (meta.type == SurQLType.RECORD):
                types.append(meta.type.value % meta.recordLink)
            else:
                types.append(meta.type.value)
        typesToken = " | ".join(types)
        if (isOptional):
            typesToken = SurQLType.OPTIONAL.value % typesToken
        tokens.append(typesToken)
        fieldSDL =  " ".join(tokens) + ";"
        return "\n".join([fieldSDL] + [d.sdl for d in self.definitions])

SchemaField.model_rebuild()