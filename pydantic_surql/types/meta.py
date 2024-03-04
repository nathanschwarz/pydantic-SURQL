from __future__ import annotations
from datetime import datetime
from enum import Enum
from types import GenericAlias, NoneType
from typing import Any, Optional, Type, get_args
from pydantic import BaseModel, ConfigDict, Field, field_serializer
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
    def from_pydantic_model(model: BaseType, name: str) -> Schema:
        """
            Create a schema from a pydantic model
        """
        fields = []
        for field_name, field in model.model_fields.items():
            fieldName = name + '.' + field_name if name is not None else field_name
            _field = SchemaField.from_type(fieldName, field.annotation)
            fields.append(_field)
        schema = Schema(fields=fields)
        return schema

    @property
    def sdl(self) -> str:
        """
            Get the SDL representation of the schema
        """
        return "\n".join([field.sdl for field in self.fields])


class MetaType(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    type: SurQLType
    original: Type | GenericAlias | Optional[Any]
    subType: Type | GenericAlias | Optional[Any] | None = None

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
        return self.type is SurQLType.OBJECT and (
            self.original == dict
            or self.original.model_config.get('extra') == 'allow'
        )

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
        if (issubclass(type, BaseModel) or type == dict):
            return SurQLType.OBJECT
        raise ValueError(f"Type {type} is not supported")

    @staticmethod
    def from_type(originalType: Type) -> MetaType:
        """
            Create a schema field meta from a type
        """
        _type = MetaType.__get_type(originalType)
        subType = None
        if (_type == SurQLType.ARRAY):
            subType = get_args(originalType)[0]
        elif (_type == SurQLType.SET):
            subType = get_args(originalType)[0]
        return MetaType(
            type=_type,
            original=originalType,
            subType=subType
        )

class TypeTree(BaseModel):
    types: list[str] = []
    definitions: list[SchemaField] = []
    isFlexible: bool = False
    isOptional: bool = False

    def type(self) -> str:
        """
            Get the SDL representation of the type tree
        """
        type_str = "|".join(self.types)
        if (self.isOptional):
            return (SurQLType.OPTIONAL.value % type_str)
        return type_str

class SchemaField(BaseModel):
    """
        A simple schema field definition
    """
    name: str
    metas: list[MetaType] = Field(min_length=1)
    definitions: list[Schema | SchemaField] = []

    @staticmethod
    def from_type(name: str, type: Type) -> SchemaField:
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
                    definitions.append(Schema.from_pydantic_model(type, name))
                else:
                    # is a list or set
                    definitions.append(SchemaField.from_type(f"{name}.*", meta.subType))
        return SchemaField(name=name, metas=metas, definitions=definitions)

    @property
    def isOptional(self) -> bool:
        """
            Check if the field is optional
        """
        return any([m.type == SurQLType.OPTIONAL for m in self.metas])

    @property
    def types(self) -> list[SurQLType]:
        """
            Get the type of the field
        """
        return [m.type for m in self.metas]

    @property
    def table(self) -> str:
        """
            Get the table name of the field
        """
        return self.name.split('.')[0]

    @property
    def field_path(self) -> str:
        """
            Get the field path
        """
        return self.name.replace(self.table + '.', '', 1)

    @property
    def type_tree(self) -> TypeTree:
        """
            Get the flat tree of the schema field
        """
        tree = TypeTree()
        for idx, meta in enumerate(self.metas):
            if (meta.type == SurQLType.OPTIONAL):
                tree.isOptional = True
            elif (meta.type == SurQLType.RECORD):
                tree.types.append(meta.type.value % meta.recordLink)
            elif (meta.type == SurQLType.ARRAY or meta.type == SurQLType.SET):
                _tree = self.definitions[idx].type_tree
                tree.types.append(meta.type.value % _tree.type())
                tree.definitions.extend(_tree.definitions)
                tree.isFlexible = tree.isFlexible or _tree.isFlexible
            elif (meta.type == SurQLType.OBJECT):
                tree.isFlexible = tree.isFlexible or meta.flexible
                tree.types.append(meta.type.value)
                tree.definitions.append(self.definitions[idx])
            elif (meta.type == SurQLType.ENUM):
                tree.types.extend([SurQLType.STRING.value, SurQLType.NUMBER.value])
            else:
                tree.types.append(meta.type.value)
        return tree

    @property
    def sdl(self) -> str:
        """
            Get the SDL representation of the schema field
        """
        tokens: list[str] = [f"DEFINE FIELD {self.field_path} ON TABLE {self.table}"]
        tree = self.type_tree
        tokens.append("FLEXIBLE TYPE" if tree.isFlexible else "TYPE")
        tokens.append(tree.type())
        fieldSDL =  " ".join(tokens) + ";"
        return "\n".join([fieldSDL] + [d.sdl for d in tree.definitions])

SchemaField.model_rebuild()