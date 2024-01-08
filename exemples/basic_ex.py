from enum import Enum
from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel
from datetime import datetime
from typing import Any

class BasicEnum(Enum):
    ONE = "ONE"
    TWO = "TWO"
    THREE = "THREE"
    FOUR = 4
    FIVE = 5
    SIX = 6

@surql_collection("basic_types")
class BasicTypes(BaseModel):
    id: str
    string: str
    number: int
    number_two: float
    date: datetime
    flag: bool
    any_v: Any
    enum_v: BasicEnum


print(Metadata.collect())