from pydantic_surql import surql_collection, Metadata
from pydantic_surql.types import SurQLAnyRecord
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

@surql_collection("generic_record_types")
class GenericRecordTypes(BaseModel):
  id: str
  record_target: SurQLAnyRecord
  #...

print(Metadata.collect())