# Pydantic-SURQL

Pydantic Surql is a utility set to automatically convert Pydantic models to SURQL SDL definitions.

✅ it supports the following features

- [collection definitions (a.k.a tables)](#collections-definitions)
  - [schemafull / schemaless](#schemafull--schemaless-definitions)
  - [drop](#drop-definitions)
  - [changefeed](#changefeed-definitions)
  - [view](#view-definitions)
  - [indexes definitions](#indexes-analyzers-and-tokenizers-definitions)
    - regular indexes
    - unique indexes
    - search indexes
  - [fields and tables permissions](#table-an-field-permissions)
- [analyzers definition](#indexes-analyzers-and-tokenizers-definitions)
- [tokenizers definition](#indexes-analyzers-and-tokenizers-definitions)
- [events definition](#events-definitions)

and the [following types](#types-definitions) out of the box :

- [basic types (string | int | float | boolean | datetime | any)](#basic-types)
- [union](#union-types)
- [optional and null](#optional-and-null-types)
- [array](#array-types)
- [set](#set-types)
- [object](#object-types)
- [record](#record-types)

❌ what it doesn't support yet :

- Python enums types
- Future types
- Geometry types
- SURQL queries definitions (select, update, delete, where, ...)
- SURQL functions definitions
- SURQL scopes definitions
- SURQL SDL field validation (validation goes through pydantic, too complex at this stage)

PRs are welcome 😉

## installation

To install pydantic-surql run :

```bash
pip install pydantic-surql
```

or with poetry :

```bash
poetry add pydantic-surql
```

## basic usage

to convert a pydantic model to a surql SDL definition you can use a simple decorator :

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic_surql import surql_collection

@surql_collection("writers")
class Writer(BaseModel):
    id: str
    firstname: str
    lastname: str
    birthdate: datetime


@surql_collection("books")
class Book(BaseModel):
    id: str
    title: str
    pages: Optional[int]
    description: str
    weight: float
    writer: Writer
```

All the models decorated with `@surql_collection` will be collected by the `Metadata` object, which will be used to generate the SDL.

To generate the SDL :

```python
from pydantic_surql import Metadata
models_sdl: str = Metadata.collect()
```

this will generate the following SDL :

```surql
DEFINE TABLE writers SCHEMAFULL;
DEFINE FIELD firstname ON TABLE writers TYPE string;
DEFINE FIELD lastname ON TABLE writers TYPE string;
DEFINE FIELD birthdate ON TABLE writers TYPE datetime;

DEFINE TABLE books SCHEMAFULL;
DEFINE FIELD title ON TABLE books TYPE string;
DEFINE FIELD pages ON TABLE books TYPE optional<number>;
DEFINE FIELD description ON TABLE books TYPE string;
DEFINE FIELD weight ON TABLE books TYPE number;
DEFINE FIELD writer ON TABLE books TYPE record<writers>;
```

## Collections definitions

### schemafull / schemaless definitions

By default collections are schemafull because pydantic doesn't allow models to have extra values.\
to make a collection schemaless you can use [pydantic built in feature](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.extra).

```python
from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel, ConfigDict

@surql_collection("schemaless_collection")
class SchemaLessCollection(BaseModel):
  model_config = ConfigDict(extra='allow')
  #...

print(Metadata.collect())
```

or

```python
from pydantic_surql import surql_collection, Metadata
from pydantic_surql.types import SurQLTableConfig
from pydantic import BaseModel, ConfigDict

@surql_collection("schemaless_collection", SurQLTableConfig(strict=False))
class SchemaLessCollection(BaseModel):
  pass

print(Metadata.collect())
```

> [!NOTE]
> the `model_config.extra` value will prime on conflict.
>
> if `strict == False` and `model_config.extra != 'allow'` it will be set to `allow` automatically

this will generate the following SDL :

```surql
DEFINE TABLE schemaless_collection SCHEMALESS;
```

### drop definitions

you can define the collection as dropped through the config :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic_surql.types import SurQLTableConfig
from pydantic import BaseModel

@surql_collection("drop_collection", SurQLTableConfig(drop=True))
class DropCollection(BaseModel):
  pass

print(Metadata.collect())
```

this will generate the following SDL :

```surql
DEFINE TABLE drop_collection DROP SCHEMAFULL;
```

### changefeed definitions

you can define the changefeed on collection through the config :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic_surql.types import SurQLTableConfig
from pydantic import BaseModel

@surql_collection("changefeed_collection", SurQLTableConfig(changeFeed="1d"))
class ChangefeedCollection(BaseModel):
  pass

print(Metadata.collect())
```

this will generate the following SDL :

```surql
DEFINE TABLE changefeed_collection SCHEMAFULL CHANGEFEED 1d;
```

### view definitions

you can define a collection as a view through the config :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic_surql.types import SurQLTableConfig, SurQLView
from pydantic import BaseModel

config = SurQLTableConfig(asView=SurQLView(select=["name", "age"], from_t=["users"], where=["age > 18"], group_by=["age"]))
@surql_collection("view_collection", config)
class ViewCollection(BaseModel):
  name: list[str]
  age: str

print(Metadata.collect())
```

this will generate the following SDL :

```surql
DEFINE TABLE view_collection AS SELECT name,age FROM users WHERE age > 18 GROUP BY age;
```

### indexes, analyzers and tokenizers definitions

You can define indexes on collections through the config :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel, ConfigDict
from pydantic_surql.types import (
  SurQLTableConfig,
  SurQLIndex,
  SurQLUniqueIndex,
  SurQLSearchIndex,
  SurQLAnalyzer,
  SurQLTokenizers
)

index = SurQLIndex(name="index_name", fields=["field1", "field2"])
unique_index = SurQLUniqueIndex(name="unique_index_name", fields=["field1", "field2"])
analyzer = SurQLAnalyzer(name="analyzer_name", tokenizers=[SurQLTokenizers.BLANK])
search_index = SurQLSearchIndex(
  name="search_index_name",
  fields=["field3"],
  analyzer=analyzer,
  highlights=True
)

@surql_collection("indexed_collection", SurQLTableConfig(indexes=[index, unique_index, search_index]))
class IndexedCollection(BaseModel):
    field1: str
    field2: str
    field3: str

print(Metadata.collect())
```

this will generate the following SDL :

```surql
DEFINE ANALYZER analyzer_name TOKENIZERS blank;

DEFINE TABLE indexed_collection SCHEMAFULL;
DEFINE FIELD field1 ON TABLE indexed_collection TYPE string;
DEFINE FIELD field2 ON TABLE indexed_collection TYPE string;
DEFINE FIELD field3 ON TABLE indexed_collection TYPE string;
DEFINE INDEX index_name ON TABLE indexed_collection FIELDS field1,field2;
DEFINE INDEX unique_index_name ON TABLE indexed_collection FIELDS field1,field2 UNIQUE;
DEFINE INDEX search_index_name ON TABLE indexed_collection FIELDS field3 SEARCH ANALYZER analyzer_name HIGHLIGHTS;
```

> [!NOTE]
> only the used tokenizers (used in a configuration) will be collected

### table an field permissions

You can define permissions on collections through the config :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel, ConfigDict
from pydantic_surql.types import (
  SurQLTableConfig,
  SurQLPermissions,
)

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
```

this will generate the following SDL :

```surql
DEFINE TABLE permission_collection SCHEMAFULL PERMISSIONS
    FOR SELECT
        WHERE published = true
        OR user = $auth.id
    FOR CREATE
        WHERE user = $auth.id
    FOR UPDATE
        WHERE user = $auth.id
    FOR DELETE
        WHERE user = $auth.id
        OR $auth.admin = true;
DEFINE FIELD field1 ON TABLE permission_collection TYPE string;
DEFINE FIELD field2 ON TABLE permission_collection TYPE string;
DEFINE FIELD field3 ON TABLE permission_collection TYPE string;
DEFINE FIELD published ON TABLE permission_collection TYPE bool;
```

You can define field permissions throught the `SurQLFieldConfig` function.\
it's a wrapper around the pydantic `Field` function (so you can use all the properties from the `Field` definition) :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel, ConfigDict
from pydantic_surql.types import (
  SurQLTableConfig,
  SurQLPermissions,
  SurQLFieldConfig
)

fields_permission = SurQLPermissions(
    select=["WHERE user = $auth.id"],
    create=["WHERE user = $auth.id"],
    update=["WHERE user = $auth.id"],
    delete=["WHERE user = $auth.id", "OR $auth.admin = true"]
)
@surql_collection("permission_collection", permission_config)
class FieldPermissionsCollection(BaseModel):
    field1: str = SurQLFieldConfig(permissions=fields_permission, min_length=2)
    field2: str
    field3: str
    published: bool

print(Metadata.collect())
```

this will generate the following SDL:

```surql
DEFINE FIELD field1 ON TABLE field_permission_collection TYPE string PERMISSIONS
    FOR SELECT
        WHERE user = $auth.id
    FOR CREATE
        WHERE user = $auth.id
    FOR UPDATE
        WHERE user = $auth.id
    FOR DELETE
        WHERE user = $auth.id
        OR $auth.admin = true;
DEFINE FIELD field2 ON TABLE field_permission_collection TYPE string;
DEFINE FIELD field3 ON TABLE field_permission_collection TYPE string;
DEFINE FIELD published ON TABLE field_permission_collection TYPE bool;
```

## events definitions

You can define events through the collection config :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel, ConfigDict
from pydantic_surql.types import SurQLTableConfig, SurQLEvent

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
```

this will generate the following SDL:

```surql
DEFINE ANALYZER analyzer_name TOKENIZERS blank;

DEFINE TABLE event_collection SCHEMAFULL;
DEFINE FIELD field1 ON TABLE event_collection TYPE string;
DEFINE FIELD field2 ON TABLE event_collection TYPE string;
DEFINE FIELD field3 ON TABLE event_collection TYPE string;
DEFINE EVENT event_name ON TABLE event_collection WHEN $event = "INSERT" OR $event = "UPDATE" THEN (INSERT INTO notification_collection (name, collection) VALUES ('something changed', 'event_collection'));
```

## Types definitions

### basic types

to define a basic type you can use the following python types :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel
from datetime import datetime
from typing import Any

@surql_collection("basic_types")
class BasicTypes(BaseModel):
    id: str
    string: str
    number: int
    number_two: float
    date: datetime
    flag: bool
    any_v: Any

print(Metadata.collect())
```

this will generate the following SDL:

```surql
DEFINE TABLE basic_types SCHEMAFULL;
DEFINE FIELD string ON TABLE basic_types TYPE string;
DEFINE FIELD number ON TABLE basic_types TYPE number;
DEFINE FIELD number_two ON TABLE basic_types TYPE number;
DEFINE FIELD date ON TABLE basic_types TYPE datetime;
DEFINE FIELD flag ON TABLE basic_types TYPE bool;
DEFINE FIELD any_v ON TABLE basic_types TYPE any;
```

### union types

to define union types you can use the `Union[T, Y]` or the `|` notation :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel
from typing import Union
from datetime import datetime

@surql_collection("union_types")
class UnionTypes(BaseModel):
    id: str
    str_number: Union[str, int]
    date_timestamp: int | datetime
    #...

print(Metadata.collect())
```

this will generate the following SDL:

```surql
DEFINE TABLE union_types SCHEMAFULL;
DEFINE FIELD str_number ON TABLE union_types TYPE string|number;
DEFINE FIELD date_timestamp ON TABLE union_types TYPE number|datetime;
```

### optional and null types

to define an optional type you can use the `Optional` notation :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic import BaseModel
from typing import Optional

@surql_collection("optional_types")
class OptionalTypes(BaseModel):
    id: str
    opt_str: Optional[str]
    #...

print(Metadata.collect())
```

this will generate the following SDL:

```surql
DEFINE TABLE optional_types SCHEMAFULL;
DEFINE FIELD opt_str ON TABLE optional_types TYPE optional<string>;
```

to define a null value you can use the `SurQLNullable` type :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic_surql.types import SurQLNullable
from pydantic import BaseModel

@surql_collection("nullable_types")
class BasicTypes(BaseModel):
    id: str
    nullable_str: str | SurQLNullable
    #...

print(Metadata.collect())
```

this will generate the following SDL:

```surql
DEFINE TABLE nullable_types SCHEMAFULL;
DEFINE FIELD nullable_str ON TABLE nullable_types TYPE string|null;
```

> [!CAUTION]
> using `None` will result in an `optional` field (`Optional[T] <=> T | None`)

### array types

to define array types you can use the `list[T]` notation. \
You can nest arrays as much as you want :

```python
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
```

this will generate the following SDL:

```surql
DEFINE TABLE array_types SCHEMAFULL;
DEFINE FIELD str_list ON TABLE array_types TYPE array;
DEFINE FIELD str_list.* ON TABLE array_types TYPE string|number;
DEFINE FIELD list_str_list ON TABLE array_types TYPE array;
DEFINE FIELD list_str_list.* ON TABLE array_types TYPE array;
DEFINE FIELD list_str_list.*.* ON TABLE array_types TYPE string;
DEFINE FIELD list_list_str_list ON TABLE array_types TYPE array;
DEFINE FIELD list_list_str_list.* ON TABLE array_types TYPE array;
DEFINE FIELD list_list_str_list.*.* ON TABLE array_types TYPE array;
DEFINE FIELD list_list_str_list.*.*.* ON TABLE array_types TYPE string;
```

### set types

to define set types you can use the `set[T]` notation. \
You can nest sets as much as you want :

```python
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
```

this will generate the following SDL:

```surql
DEFINE TABLE set_types SCHEMAFULL;
DEFINE FIELD str_set ON TABLE set_types TYPE set;
DEFINE FIELD str_set.* ON TABLE set_types TYPE string|number;
DEFINE FIELD set_str_set ON TABLE set_types TYPE set;
DEFINE FIELD set_str_set.* ON TABLE set_types TYPE set;
DEFINE FIELD set_str_set.*.* ON TABLE set_types TYPE string;
DEFINE FIELD set_set_str_set ON TABLE set_types TYPE set;
DEFINE FIELD set_set_str_set.* ON TABLE set_types TYPE set;
DEFINE FIELD set_set_str_set.*.* ON TABLE set_types TYPE set;
DEFINE FIELD set_set_str_set.*.*.* ON TABLE set_types TYPE string;
```

### object types

to define an object you can use a Pydantic model. \
to mark the object as `flexible`, you can use [pydantic built in feature](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.extra) \
You can also nest objects as much as you want :

```python
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
```

this will generate the following SDL:

```surql
DEFINE TABLE object_types SCHEMAFULL;
DEFINE FIELD sub_object ON TABLE object_types TYPE object;
DEFINE FIELD sub_object.sub_sub_object ON TABLE object_types FLEXIBLE TYPE object;
DEFINE FIELD sub_object.sub_sub_object.some_mandatory_field ON TABLE object_types TYPE string;
```

> [!WARNING]
> surql doesn't support recursive objects, if you want to use recursive structures use a [`record` definition](#record-types)

### record types

Internally the `@surql_collection` decorator will mark the model as a surql collection. \
Defining a record is simple as :

```python
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
```

this will generate the following SDL:

```surql
DEFINE TABLE record_target SCHEMAFULL;
DEFINE FIELD some_field ON TABLE record_target TYPE string;

DEFINE TABLE record_types SCHEMAFULL;
DEFINE FIELD record_target ON TABLE record_types TYPE record<record_target>;
```

It's also possible to use a generic record :

```python
from pydantic_surql import surql_collection, Metadata
from pydantic_surql.types import SurQLAnyRecord
from pydantic import BaseModel

@surql_collection("generic_record_types")
class GenericRecordTypes(BaseModel):
  id: str
  record_target: SurQLAnyRecord
  #...

print(Metadata.collect())
```

this will generate the following SDL:

```surql
DEFINE TABLE generic_record_types SCHEMAFULL;
DEFINE FIELD id ON TABLE generic_record_types TYPE string;
DEFINE FIELD record_target ON TABLE generic_record_types TYPE record();
```

> [!NOTE]
> `SurQLAnyRecord <=> Type[dict]` so your pydantic model wont be able to map to pydantic classes automatically.
