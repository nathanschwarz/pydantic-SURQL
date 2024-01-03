from typing import List, Type, Set, Union
from enum import Enum
from typing import Optional
from pydantic import BaseModel

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
    DICT = "dict"
    OBJECT = "object"
    RECORD = "record"
    OPTIONAL = "optional"
    NULL = "null"

BASIC_TYPES = [
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

class SurQLField(BaseModel):
    name: Optional[str]
    types: Union[list[SurQLType | list[SurQLType]], 'SurQLField']

    def to_surql(self, table_name: str) -> List[str]:
        fieldSurql = ["TYPE"]
        fieldTypes = []
        basicTypes = [e for e in self.types if e in BASIC_TYPES]
        complexTypes = [e for e in self.types if e in COMPLEX_TYPES]
        subFields = []
        if (len(basicTypes) > 0):
            fieldTypes += [e.value for e in basicTypes]
        # for e in complexTypes:
        #     if (e == SurQLType.OBJECT):
        #         fieldTypes.append(e.value)
        #         if (self.subDef is None or len(self.subDef) == 0):
        #             fieldSurql = ["FLEXIBLE TYPE"]
        #         elif (self.subDef is SurQLType):
        #             subFields += [e.value for e in self.subDef]
        #     if (e == SurQLType.ARRAY):
        #         fieldTypes.append(e.value)
        #         subFields +=
        #     if (e == SurQLType.RECORD):
        #         print("record type not supported yet")
        #         fieldTypes.append(f"record<>")

        fieldTypes = "|".join(fieldTypes)
        if (SurQLType.OPTIONAL in self.types):
            fieldSurql += [f"optional<{fieldTypes}>"]
        else:
            fieldSurql += [fieldTypes]
        fieldSurql = " ".join(fieldSurql)
        res = [f"DEFINE FIELD {self.name} ON TABLE {table_name} {fieldSurql};"]
        return res


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