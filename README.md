# Pydantic-SURQL

Pydantic Surql is a utility set to automatically convert Pydantic models to SURQL SDL definitions.

it supports the following features

- [collection definitions (a.k.a tables)](#collections-definitions)
  - [schemafull / schemaless](#schemafull--schemaless-definitions)
  - [drop](#drop-definitions)
  - [changefeed](#changefeed-definitions)
  - [view](#view-definitions)
  - [indexes definitions](#indexes-definitions)
    - [regular indexes](#regular-indexes-definitions)
    - [unique indexes](#unique-indexes-definitions)
    - [search indexes](#search-indexes-definitions)
- [analyzers definition](#anaylizers-definitions)
- [tokenizers definition](#tokenizers-definitions)
- [events definition](#events-definitions)

and the [following types](#types-definitions) out of the box :

- [basic types (string | int | float | boolean | datetime | any)](#basic-types)
- [union](#union-types)
- [optional and null](#optional-and-null-types)
- [array](#array-types)
- [object](#object-types)
- [record](#record-types)

## installation

To install pydantic-surql run :

```bash
pip install pydantic pydantic-surql
```

or with poetry :

```bash
poetry add pydantic pydantic-surql
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
from pydantic_surql import surql_collection
from pydantic import BaseModel, ConfigDict

@surql_collection("schemaless")
class SchemaLessCollection(baseModel):
  model_config = ConfigDict(extra='allow')
  #...
```

### drop definitions

### changefeed definitions

### view definitions

### indexes definitions

#### regular indexes definitions

#### unique indexes definitions

#### search indexes definitions

## anaylizers definitions

## tokenizers definitions

## events definitions

## Types definitions

### basic types

to define a basic type you can use the following python types :

```python
from pydantic_surql import surql_collection
from pydantic import BaseModel
from datetime import datetime
from typing import Any, Optional

@surql_collection("basic_types")
class BasicTypes(BaseModel):
    id: str
    string: str
    number: int
    number_two: float
    date: datetime
    flag: bool
    any_v: Any
```

### union types

to define union types you can use the `Union[T, Y]` or the `|` notation :

```python
from pydantic_surql import surql_collection
from pydantic import BaseModel
from typing import Union
from datetime import datetime

@surql_collection("union_types")
class BasicTypes(BaseModel):
    id: str
    str_number: Union[str, int]
    date_timestamp: int | datetime
    #...
```

### optional and null types

to define an optional type you can use the `Optional` notation :

```python
from pydantic_surql import surql_collection
from pydantic import BaseModel
from typing import Optional

@surql_collection("array_types")
class BasicTypes(BaseModel):
    id: str
    opt_str: Optional[str]
    #...
```

to define a null value you can use the `SurQLNullable` type :

```python
from pydantic_surql import surql_collection
from pydantic_surql.types import SurQLNullable
from pydantic import BaseModel
from typing import Optional

@surql_collection("array_types")
class BasicTypes(BaseModel):
    id: str
    nullable_str: str | SurQLNullable
    #...
```

!!!danger using `None` will result in an `optional` field (`Optional[T] <=> T | None`)

### array types

to define array types you can use the `list[T]` notation. \
You can nest arrays as much as you want :

```python
from pydantic_surql import surql_collection
from pydantic import BaseModel

@surql_collection("array_types")
class BasicTypes(BaseModel):
    id: str
    str_list: list[str | int]
    list_str_list: list[list[str]]
    list_list_str_list: list[list[list[str]]]
    #...
```

### object types

to define an object you can use a Pydantic model. \
to mark the object as `flexible`, you can use [pydantic built in feature](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.extra) \
You can also nest objects as much as you want :

```python
from pydantic_surql import surql_collection
from pydantic import BaseModel, ConfigDict

class SubSubObject(baseModel):
  model_config = ConfigDict(extra='allow')
  some_mandatory_field: str
  #...

class SubObject(baseModel):
  sub_sub_object: SubSubObject
  #...

@surql_collection("object_types")
class ObjectTypes(BaseModel):
    id: str
    sub_object: SubObject
    #...
```

!!!warning surql doesn't support recursive objects, if you want to use recursive structures use a [`record` definition](#record-types)

### record types

Internally the `@surql_collection` decorator will mark the model as a surql collection. \
Defining a record is simple as :

```python
from pydantic_surql import surql_collection
from pydantic import BaseModel

@surql_collection("record_target")
class RecordTarget(baseModel):
  id: str
  some_field: str
  #...

@surql_collection("record_types")
class RecordTypes(BaseModel):
  id: str
  record_target: RecordTarget
  #...
```
