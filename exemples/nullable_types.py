from pydantic_surql import surql_collection, Metadata
from pydantic_surql.types import SurQLNullable
from pydantic import BaseModel

@surql_collection("nullable_types")
class BasicTypes(BaseModel):
    id: str
    nullable_str: str | SurQLNullable
    #...

print(Metadata.collect())