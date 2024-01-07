# Pydantic-SURQL

Pydantic Surql is a utility set to automatically convert Pydantic models to SURQL SDL

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
