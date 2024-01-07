from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel
from datetime import datetime
from typing import Any

@surql_collection("basic_types")
class BasicTypes(BaseModel):
    id: str
    string: str
    number: int
    number_two: float
    date: datetime
    flag: bool
    any_v: Any

print(Metadata.collect())