from typing import List, Type, Set, Union
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, model_validator
from typing_extensions import TypeAliasType

"""
    A custom type to define a nullable field
"""
SurQLNullable =  Type[None]

"""
    A custom type to define a flexible record
"""
SurQLAnyRecord = Type[dict]

class SurQLType(Enum):
    """
        SurQL types enumeration
    """
    STRING = "string"
    NUMBER = "number"
    DATE = "datetime"
    ANY = "any"
    BOOLEAN = "bool"
    ARRAY = "array"
    DICT = "FLEXIBLE TYPE object"
    OBJECT = "object"
    RECORD = "record<%s>"
    ANY_RECORD = "record()"
    OPTIONAL = "optional<%s>"
    NULL = "null"

BASIC_TYPES: list[SurQLType] = [
    SurQLType.STRING,
    SurQLType.NUMBER,
    SurQLType.ANY_RECORD,
    SurQLType.DATE,
    SurQLType.BOOLEAN,
    SurQLType.ANY,
    SurQLType.NULL,
]

COMPLEX_TYPES = [
    SurQLType.OBJECT,
    SurQLType.RECORD,
]

RecursiveType = TypeAliasType('RecursiveType', List[Union[SurQLType, 'SurQLField', 'RecursiveType']])

class SurQLField(BaseModel):
    """
        A pydantic SurQL field definition
        TODO: implement permissions
    """
    name: Optional[str]
    types: RecursiveType
    recordLink: Optional[str] = None

    @classmethod
    def _f_string(cls, field: str, table: str, types: str, isFlexible: bool):
        """
            return a SDL field definition string
        """
        return f"DEFINE FIELD {field} ON TABLE {table} {'FLEXIBLE ' if isFlexible else ''}TYPE {types};"

    @classmethod
    def surqlFromTypes(cls, table_name: str, field_name: str, types: List[Type]) -> list[str]:
        """
            return SDLS fields definitions recursively
        """
        res = []
        nextFields = []
        isOptional = False
        isFlexible = False
        for _type in types:
            if (_type in BASIC_TYPES):
                res += [_type.value]
            elif (_type is SurQLType.DICT):
                isFlexible = True
                res += [SurQLType.OBJECT.value]
            elif (isinstance(_type, list)):
                res += [SurQLType.ARRAY.value]
                nextFields += cls.surqlFromTypes(table_name, f"{field_name}.*", _type)
            elif (isinstance(_type, cls)):
                if (_type.types == [SurQLType.RECORD]):
                    res += [SurQLType.RECORD.value % _type.recordLink]
                else:
                    res += [SurQLType.OBJECT.value]
                    for _field in _type.types:
                        nextFields += cls.surqlFromTypes(table_name, f"{field_name}.{_field.name}", _field.types)
            elif (_type is SurQLType.OPTIONAL):
                isOptional = True
            else:
                raise Exception(f"Unknown type: {_type}, SDL generation not supported")
        if (isOptional):
            return [cls._f_string(field_name, table_name, SurQLType.OPTIONAL.value % "|".join(res), isFlexible)] + nextFields
        return [cls._f_string(field_name, table_name, "|".join(res), isFlexible)] + nextFields


    def SDL(self, table_name: str) -> List[str]:
        """return a SDL field definition"""
        fieldTypes = SurQLField.surqlFromTypes(table_name, self.name, self.types)
        return "\n".join(fieldTypes)


    __hash__ = object.__hash__

SurQLField.model_rebuild()

class SurQLIndex(BaseModel):
    """
        A pydantic SurQL index definition
        TODO: implement search indexes
    """
    name: str
    fields: list[str]
    unique: bool = False

    def SDL(self, table_name: str) -> str:
        """
            return a SDL index definition
        """
        return f"DEFINE INDEX {self.name} ON TABLE {table_name} {'UNIQUE' if self.unique else ''} FIELDS ({','.join(self.fields)});"

    __hash__ = object.__hash__

class SurQLView(BaseModel):
    """
        A pydantic SurQL view query definition
    """
    select: list[str]
    from_t: list[str]
    where: list[str]
    group_by: list[str]

    def SDL(self) -> str:
        """
            return a SDL view definition
        """
        _definitions = [
            "AS SELECT",
            ','.join(self.select),
            "FROM",
            ','.join(self.from_t),
            "WHERE" if len(self.where) > 0 else None,
        ] + ["GROUP BY ", ','.join(self.group_by)] if len(self.group_by) > 0 else []
        return " ".join([e for e in _definitions if e is not None]) + ';'

class SurQLTableConfig(BaseModel):
    """
        A pydantic SurQL table configuration definition
        TODO: add validation for changefeed
        TODO: implement table permissions
        TODO: implement table events
    """
    asView: SurQLView | None = Field(default=None, description="view definition")
    strict: bool = Field(default=True, description="schemafull|schemaless")
    changeFeed: str | None = Field(default=None, description="changefeed definition")
    drop: bool = Field(default=False, description="set table in DROP mode")
    indexes: Set[SurQLIndex] = Field(default_factory=set, description="table indexes definitions")


class SurQLTable(BaseModel):
    """
        A pydantic SurQL table definition
    """
    name: str
    fields: Set[SurQLField]
    config: SurQLTableConfig = SurQLTableConfig()

    def _table_def(self):
        """return a SDL schemafull table definition"""
        _definitions = [
            "DEFINE TABLE",
            self.name,
            self.config.asView.SDL() if self.config.asView is not None else None,
            "DROP" if self.config.drop else None,
            "SCHEMAFULL" if self.config.strict else "SCHEMALESS",
            f"CHANGEFEED {self.config.changeFeed}" if self.config.changeFeed is not None else None,
        ]
        return " ".join([e for e in _definitions if e is not None]) + ';'

    def SDL(self):
        """return a SDL table definition with all the fields SDL definitions"""
        res = [self._table_def()]
        if (self.config.asView is None):
            for field in self.fields:
                res.append(field.SDL(self.name))
            for index in self.config.indexes:
                res.append(index.SDL(self.name))
        return "\n".join(res)

    __hash__ = object.__hash__

class SurQLMapper(BaseModel):
    """
        A simple mapper to store all the SurQL tables definitions generated from pydantic models
    """
    tables: Set[SurQLTable]
    __hash__ = object.__hash__