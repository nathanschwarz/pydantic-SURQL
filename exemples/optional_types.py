from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel
from typing import Optional

@surql_collection("optional_types")
class OptionalTypes(BaseModel):
    id: str
    opt_str: Optional[str]
    #...

print(Metadata.collect())