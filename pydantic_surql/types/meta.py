from __future__ import annotations
from functools import reduce
from datetime import datetime
from enum import Enum
from types import GenericAlias, NoneType
from typing import Any, ClassVar, Optional, Type, Union, get_args

from pydantic import BaseModel, ConfigDict, Field, create_model, field_serializer, computed_field
from pydantic.fields import FieldInfo

from pydantic_surql.types.config import SurQLTableConfig
from pydantic_surql.types.utils import SurQLAnyRecord, SurQLNullable, is_union, SurQLType
from pydantic_surql.types.fieldInfo import SurQLFieldInfo
from pydantic_surql.types.permissions import SurQLPermissions

class Input(BaseModel):
    """
        A simple input definition
    """
    @staticmethod
    def parse_field_type(field: SchemaField):
        types = []
        isOptional = False
        for idx, meta in enumerate(field.metas):
            if (meta.type == SurQLType.SET):
                types.append(set[Input.parse_field_type(field.definitions[idx])])
            elif (meta.type == SurQLType.ARRAY):
                types.append(list[Input.parse_field_type(field.definitions[idx])])
            elif (meta.type == SurQLType.RECORD):
                types.append(str)
            elif (meta.type == SurQLType.OBJECT):
                types.append(Input.from_schema(field.definitions[idx], field.definitions[idx].name))
            elif (meta.type == SurQLType.NULL):
                types.append(NoneType)
            elif (meta.type == SurQLType.OPTIONAL):
                isOptional = True
            else:
                # int | float | str | bool | datetime | Enum | Any
                types.append(meta.original)
        if (len(types) > 1):
            types = reduce(lambda x, y: x | y, types)
        else:
            types = types[0]
        if (isOptional):
            return Optional[types]
        return types

    @staticmethod
    def from_schema(schema: Schema, model_name: str) -> Type[Input]:
        """
            Create an input from a schema
        """
        fields = {}
        for field in schema.fields:
            type = Input.parse_field_type(field)
            isDiff = type != field.info.annotation
            fields[field.name] = (type, FieldInfo(
                default=isDiff and None or field.info.default,
                default_factory=isDiff and None or field.info.default_factory,
                alias=field.info.alias,
                alias_priority=field.info.alias_priority,
                validation_alias=field.info.validation_alias,
                serialization_alias=field.info.serialization_alias,
                title=field.name,
                description=field.info.description,
                examples=isDiff and None or field.info.examples,
                exclude=field.info.exclude,
                discriminator=field.info.discriminator,
                json_schema_extra=field.info.json_schema_extra,
                frozen=field.info.frozen,
                validate_default=field.info.validate_default,
                repr=field.info.repr,
                init_var=field.info.init_var,
                kw_only=field.info.kw_only,
                metadata=field.info.metadata
            ))
        input = create_model(
            __model_name= model_name + "Input",
            __base__=(Input),
            __doc__=f"Input for the model {model_name}",
            model_config = ConfigDict(extra=schema.isFlexible and 'allow' or 'forbid'),
            **fields
        )
        return input

class BaseType(BaseModel):
    is_surql_collection: ClassVar[bool]
    surql_table_name: ClassVar[str]
    surql_schema: ClassVar[Schema]
    surql_config: ClassVar[SurQLTableConfig]
    input: ClassVar[Type[Input]]

class Schema(BaseModel):
    """
        A simple schema definition
    """
    fields: list[SchemaField]
    name: str
    isFlexible: bool = False

    @staticmethod
    def from_pydantic_model(model: BaseType, name: str) -> Schema:
        """
            Create a schema from a pydantic model
        """
        fields = []
        isFlexible = model.model_config.get('extra') == 'allow'
        for field_name, field in model.model_fields.items():
            if (field_name != "id"):
                path = name + '.' + field_name if name is not None else field_name
                _field = SchemaField.from_type(field_name, path, field.annotation, field)
                fields.append(_field)
        schema = Schema(fields=fields, isFlexible=isFlexible, name=model.__qualname__)
        return schema

    @computed_field
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

    @computed_field
    def flexible(self) -> bool:
        """
            Check if the field is flexible
        """
        return self.type is SurQLType.OBJECT and (
            self.original == dict
            or self.original.model_config.get('extra') == 'allow'
        )

    @computed_field
    def recordLink(self) -> str | None:
        """
            Get the record link
        """
        return self.original.surql_table_name if self.type is SurQLType.RECORD else None

    @computed_field
    def assertions(self) -> Optional[str]:
        """
            Get the assertion
        """
        if (self.type == SurQLType.ENUM):
            __assertions = ",".join([f'"{item.value}"' if isinstance(item.value, str) else str(item.value) for item in self.original])
            return f"$value in [{__assertions}]"
        return None

    @computed_field
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
    model_config = ConfigDict(arbitrary_types_allowed=True)
    name: str | None
    path: str
    metas: list[MetaType] = Field(min_length=1)
    definitions: list[Schema | SchemaField] = []
    info: FieldInfo | Type[FieldInfo] | None = None

    @staticmethod
    def from_type(name: str, path: str, type: Type, field: FieldInfo | Type[FieldInfo] | None = None) -> SchemaField:
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
                    definitions.append(Schema.from_pydantic_model(type, path))
                else:
                    # is a list or set
                    definitions.append(SchemaField.from_type(None, f"{path}.*", meta.subType))
        return SchemaField(name=name, path=path, metas=metas, definitions=definitions, info=field)

    @computed_field
    def perms(self) -> Optional[SurQLPermissions]:
        """
            Get the permissions
        """
        return self.metas[0].original.perms if isinstance(self.metas[0].original, SurQLFieldInfo) else None

    @computed_field
    def isOptional(self) -> bool:
        """
            Check if the field is optional
        """
        return any([m.type == SurQLType.OPTIONAL for m in self.metas])

    @computed_field
    def types(self) -> list[SurQLType]:
        """
            Get the type of the field
        """
        return [m.type for m in self.metas]

    @computed_field
    def table(self) -> str:
        """
            Get the table name of the field paths
        """
        return self.path.split('.')[0]

    @computed_field
    def field_path(self) -> str:
        """
            Get the field path (without the table name)
        """
        return self.path.replace(self.table + '.', '', 1)

    @computed_field
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
                _tree: TypeTree = self.definitions[idx].type_tree
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

    @computed_field
    def sdl(self) -> str:
        """
            Get the SDL representation of the schema field
            TODO: handle assertions
        """
        tokens: list[str] = [f"DEFINE FIELD {self.field_path} ON TABLE {self.table}"]
        tree: TypeTree = self.type_tree
        tokens.append("FLEXIBLE TYPE" if tree.isFlexible else "TYPE")
        tokens.append(tree.type())
        if (self.perms is not None):
            tokens.append("\n" + self.perms.SDL())
        fieldSDL =  " ".join(tokens) + ";"
        return "\n".join([fieldSDL] + [d.sdl for d in tree.definitions])

SchemaField.model_rebuild()