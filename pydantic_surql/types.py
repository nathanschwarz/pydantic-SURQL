from types import GenericAlias
from typing import List, Type, Set, Union, get_args
from enum import Enum
from typing import Optional
from pydantic import BaseModel
from typing_extensions import TypeAliasType

SurQLNullable = Type[None]

class SurQLType(Enum):
    """
        SurQL types enumeration
        note:
        the DICT type is equivalent to a flexible object
        the OBJECT type is equivalent to a schemafull object
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
    OPTIONAL = "optional<%s>"
    NULL = "null"

BASIC_TYPES: list[SurQLType] = [
    SurQLType.STRING,
    SurQLType.NUMBER,
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
    name: Optional[str]
    types: RecursiveType
    recordLink: Optional[str] = None

    @classmethod
    def _f_string(cls, field: str, table: str, types: str):
        return f"DEFINE FIELD {field} ON TABLE {table} TYPE {types};"

    @classmethod
    def surqlFromTypes(cls, table_name: str, field_name: str, types: List[Type]) -> list[str]:
        res = []
        nextFields = []
        isOptional = False
        for _type in types:
            if (_type in BASIC_TYPES):
                res += [_type.value]
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
            #else:
                # print(_type)
                # print("\n")
        if (isOptional):
            return [cls._f_string(field_name, table_name, SurQLType.OPTIONAL.value % "|".join(res))] + nextFields
        return [cls._f_string(field_name, table_name, "|".join(res))] + nextFields


    def to_surql(self, table_name: str) -> List[str]:
        fieldTypes = SurQLField.surqlFromTypes(table_name, self.name, self.types)
        return "\n".join(fieldTypes)


    __hash__ = object.__hash__

SurQLField.model_rebuild()

class SurQLTable(BaseModel):
    name: str
    fields: Set[SurQLField]

    def _table_def(self):
        return f"DEFINE TABLE {self.name} SCHEMAFULL;"

    def to_surql(self):
        res = [self._table_def()]
        for field in self.fields:
            res.append(field.to_surql(self.name))
        return "\n".join(res)


    __hash__ = object.__hash__

class SurQLMapper(BaseModel):
    tables: Set[SurQLTable]