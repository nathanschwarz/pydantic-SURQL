from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel

@surql_collection("array_types")
class ArrayTypes(BaseModel):
    id: str
    str_list: list[str | int]
    list_str_list: list[list[str]]
    list_list_str_list: list[list[list[str]]]
    #...

print(Metadata.collect())