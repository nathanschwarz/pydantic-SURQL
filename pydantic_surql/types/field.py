from typing import List, Type, Union, Sequence
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from typing_extensions import TypeAliasType

from .permissions import SurQLPermissions

"""
    A custom type to define a nullable field
"""
SurQLNullable =  Type[None]

"""
    A custom type to define a generic record
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
    OBJECT = "object"
    SET = "set"
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

RecursiveType = TypeAliasType('RecursiveType', Sequence[Union[SurQLType, 'SurQLField', 'RecursiveType']])

class SurQLField(BaseModel):
    """
        A pydantic SurQL field definition
        TODO: implement permissions
    """
    name: Optional[str]
    types: RecursiveType
    recordLink: Optional[str] = None
    isFlexible: bool = False
    perms: Optional[SurQLPermissions] = None

    @classmethod
    def _f_string(cls, field: str, table: str, types: str, isFlexible: bool, perms: Optional[SurQLPermissions] = None):
        """
            return a SDL field definition string
        """
        return " ".join(e for e in [
            f"DEFINE FIELD {field} ON TABLE {table} {'FLEXIBLE ' if isFlexible else ''}TYPE {types}",
            perms.SDL() if perms is not None else None
        ] if e != None) + ";"

    @classmethod
    def _surqlFromTypes(cls, table_name: str, field_name: str, types: List[Type], perms: Optional[SurQLPermissions] = None) -> list[str]:
        """
            return SDLS fields definitions recursively
            TODO: remove duplicates (eg: when a field is defined as int | float)
            TODO: check name is not a reserved keyword
        """
        res = []
        nextFields = []
        isOptional = False
        isFlexible = False
        for _type in types:
            if (_type in BASIC_TYPES):
                res += [_type.value]
            elif isinstance(_type, list):
                if (_type[0] == SurQLType.SET):
                    res += [SurQLType.SET.value]
                    nextFields += cls._surqlFromTypes(table_name, f"{field_name}.*", _type[1])
                else:
                    res += [SurQLType.ARRAY.value]
                    _perms = getattr(_type, "perms", None)
                    nextFields += cls._surqlFromTypes(table_name, f"{field_name}.*", _type, _perms)
            elif (isinstance(_type, cls)):
                if (_type.types == [SurQLType.RECORD]):
                    res += [SurQLType.RECORD.value % _type.recordLink]
                else:
                    res += [SurQLType.OBJECT.value]
                    isFlexible = _type.isFlexible
                    for _field in _type.types:
                        _perms = getattr(_field, "perms", None)
                        nextFields += cls._surqlFromTypes(table_name, f"{field_name}.{_field.name}", _field.types, _perms)
            elif (_type is SurQLType.OPTIONAL):
                isOptional = True
            else:
                raise Exception(f"Unknown type: {_type}, SDL generation not supported")
        if (isOptional):
            return [cls._f_string(field_name, table_name, SurQLType.OPTIONAL.value % "|".join(res), isFlexible, perms)] + nextFields
        return [cls._f_string(field_name, table_name, "|".join(res), isFlexible, perms)] + nextFields


    def SDL(self, table_name: str) -> List[str]:
        """return a SDL field definition"""
        fieldTypes = SurQLField._surqlFromTypes(table_name, self.name, self.types, self.perms)
        return "\n".join(fieldTypes)


    __hash__ = object.__hash__

SurQLField.model_rebuild()

class SurQLFieldInfo(FieldInfo):
    """
        A pydantic SurQL field info definition
    """
    perms: Optional[SurQLPermissions] = None

    def __init__(self, perms: Optional[SurQLPermissions], **kwargs):
        super().__init__(**kwargs)
        self.perms = perms

def SurQLFieldConfig(permissions: Optional[SurQLPermissions] = None, **kwargs) -> SurQLFieldInfo:
    """
        A pydantic SurQL field config definition
        TODO: find a way to map Field arguments for proper type hints (see: https://stackoverflow.com/questions/1409295/set-function-signature-in-python)
    """
    return SurQLFieldInfo(permissions, *kwargs)