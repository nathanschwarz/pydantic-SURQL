from pydantic import BaseModel
from pydantic_surql import surql_collection, Metadata

@surql_collection("array_types")
class ArrayTypes(BaseModel):
    id: str
    str_list: list[str | int]
    list_str_list: list[list[str]]
    list_list_str_list: list[list[list[str]]]
    #...

print(Metadata.collect())

Metadata.clear()
from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel

@surql_collection("set_types")
class SetTypes(BaseModel):
    id: str
    str_set: set[str | int]
    set_str_set: set[set[str]]
    set_set_str_set: set[set[set[str]]]
    #...

print(Metadata.collect())