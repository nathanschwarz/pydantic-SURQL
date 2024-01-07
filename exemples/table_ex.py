from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel, ConfigDict
from pydantic_surql.types import SurQLTableConfig, SurQLView

@surql_collection("schemaless")
class SchemaLessCollection(BaseModel):
  model_config = ConfigDict(extra='allow')
  #...

from pydantic_surql import surql_collection, Metadata
print(Metadata.collect())

Metadata.clear()
@surql_collection("schemaless", SurQLTableConfig(strict=False))
class SchemaLessConfCollection(BaseModel):
  pass

print(Metadata.collect())


Metadata.clear()
@surql_collection("drop_collection", SurQLTableConfig(drop=True))
class DropCollection(BaseModel):
  pass

print(Metadata.collect())


Metadata.clear()
@surql_collection("changefeed_collection", SurQLTableConfig(changeFeed="1d"))
class ChangefeedCollection(BaseModel):
  pass

print(Metadata.collect())

Metadata.clear()
config = SurQLTableConfig(asView=SurQLView(select=["name", "age"], from_t=["users"], where=["age > 18"], group_by=["age"]))
@surql_collection("view_collection", config)
class ViewCollection(BaseModel):
  name: list[str]
  age: str

print(Metadata.collect())