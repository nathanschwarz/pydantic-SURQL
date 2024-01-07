from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel, ConfigDict

class SubSubObject(BaseModel):
  model_config = ConfigDict(extra='allow')
  some_mandatory_field: str
  #...

class SubObject(BaseModel):
  sub_sub_object: SubSubObject
  #...

@surql_collection("object_types")
class ObjectTypes(BaseModel):
    id: str
    sub_object: SubObject
    #...

print(Metadata.collect())
