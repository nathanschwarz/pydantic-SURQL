from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel

@surql_collection("record_target")
class RecordTarget(BaseModel):
  id: str
  some_field: str
  #...

@surql_collection("record_types")
class RecordTypes(BaseModel):
  id: str
  record_target: RecordTarget
  #...

print(Metadata.collect())