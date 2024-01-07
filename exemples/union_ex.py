from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel
from typing import Union
from datetime import datetime

@surql_collection("union_types")
class UnionTypes(BaseModel):
    id: str
    str_number: Union[str, int]
    date_timestamp: int | datetime
    #...

print(Metadata.collect())