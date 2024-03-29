from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel, ConfigDict
from pydantic_surql.types import SurQLTableConfig, SurQLView, SurQLEvent, SurQLFieldConfig, SurQLPermissions

# schemaless

@surql_collection("schemaless_collection")
class SchemaLessCollection(BaseModel):
  model_config = ConfigDict(extra='allow')
  #...

from pydantic_surql import surql_collection, Metadata
print(Metadata.collect())

Metadata.clear()
@surql_collection("schemaless_collection", SurQLTableConfig(strict=False))
class SchemaLessConfCollection(BaseModel):
  pass

print(Metadata.collect())

# drop

Metadata.clear()
@surql_collection("drop_collection", SurQLTableConfig(drop=True))
class DropCollection(BaseModel):
  pass

print(Metadata.collect())

# changefeed

Metadata.clear()
@surql_collection("changefeed_collection", SurQLTableConfig(changeFeed="1d"))
class ChangefeedCollection(BaseModel):
  pass

print(Metadata.collect())

# view

Metadata.clear()
config = SurQLTableConfig(asView=SurQLView(select=["name", "age"], from_t=["users"], where=["age > 18"], group_by=["age"]))
@surql_collection("view_collection", config)
class ViewCollection(BaseModel):
  name: list[str]
  age: str

print(Metadata.collect())

# events

Metadata.clear()
event_config = SurQLTableConfig(events=[
  SurQLEvent(
    name="event_name",
    whenSDL=["$event = \"INSERT\"", "$event = \"UPDATE\""],
    querySDL="INSERT INTO notification_collection (name, collection) VALUES ('something changed', 'event_collection')"
  )])
@surql_collection("event_collection", event_config)
class EventCollection(BaseModel):
    field1: str
    field2: str
    field3: str

print(Metadata.collect())

# permissions

Metadata.clear()
permission_config = SurQLTableConfig(
   permissions=SurQLPermissions(
    select=["WHERE published = true", "OR user = $auth.id"],
    create=["WHERE user = $auth.id"],
    update=["WHERE user = $auth.id"],
    delete=["WHERE user = $auth.id", "OR $auth.admin = true"]
  )
)
@surql_collection("permission_collection", permission_config)
class PermissionCollection(BaseModel):
    field1: str
    field2: str
    field3: str
    published: bool

print(Metadata.collect())

Metadata.clear()
fields_permission = SurQLPermissions(
    select=["WHERE user = $auth.id"],
    create=["WHERE user = $auth.id"],
    update=["WHERE user = $auth.id"],
    delete=["WHERE user = $auth.id", "OR $auth.admin = true"]
)
@surql_collection("field_permission_collection")
class FieldPermissionsCollection(BaseModel):
    field1: str = SurQLFieldConfig(permissions=fields_permission, min_length=2)
    field2: str
    field3: str
    published: bool

print(Metadata.collect())