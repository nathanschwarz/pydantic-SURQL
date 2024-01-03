from typing import Type, Set
from enum import Enum
from typing import Optional
from pydantic import BaseModel

SchemaType = Type[BaseModel]
SurQLNullable = Type[None]

class SurQLType(Enum):
    STRING = "string"
    NUMBER = "number"
    DATE = "datetime"
    BOOLEAN = "bool"
    ARRAY = "array"
    OBJECT = "object"
    RECORD = "record"
    OPTIONAL = "optional"
    NULL = "null"

class SurQLField(BaseModel):
    name: Optional[str]
    types: list[SurQLType]
    subDef: Optional[list[SurQLType] | SurQLType | SchemaType | 'SurQLField']

SurQLField.model_rebuild()

class SurQLTable(BaseModel):
    name: str
    fields: Set[SurQLField]

class SurQLMapper(BaseModel):
    tables: Set[SurQLTable]