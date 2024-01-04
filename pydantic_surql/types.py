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
    """
        A pydantic SurQL field definition
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
            if (_type is SurQLType.DICT):
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
            #else:
                # print(_type)
                # print("\n")
        if (isOptional):
            return [cls._f_string(field_name, table_name, SurQLType.OPTIONAL.value % "|".join(res), isFlexible)] + nextFields
        return [cls._f_string(field_name, table_name, "|".join(res), isFlexible)] + nextFields


    def to_surql(self, table_name: str) -> List[str]:
        """return a SDL field definition"""
        fieldTypes = SurQLField.surqlFromTypes(table_name, self.name, self.types)
        return "\n".join(fieldTypes)


    __hash__ = object.__hash__

SurQLField.model_rebuild()

class SurQLTable(BaseModel):
    """
        A pydantic SurQL table definition
        TODO: implement indexes definitions (unique, search)
        TODO: implement views definitions
        TODO: implement table permissions
    """
    name: str
    fields: Set[SurQLField]

    def _table_def(self):
        """return a SDL schemafull table definition"""
        return f"DEFINE TABLE {self.name} SCHEMAFULL;"

    def to_surql(self):
        """return a SDL table definition with all the fields SDL definitions"""
        res = [self._table_def()]
        for field in self.fields:
            res.append(field.to_surql(self.name))
        return "\n".join(res)


    __hash__ = object.__hash__

class SurQLMapper(BaseModel):
    """
        A simple mapper to store all the SurQL tables definitions generated from pydantic models
    """
    tables: Set[SurQLTable]