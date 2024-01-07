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