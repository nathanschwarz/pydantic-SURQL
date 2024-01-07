from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from pydantic_surql import surql_collection, Metadata

@surql_collection("writers")
class Writer(BaseModel):
    firstname: str
    lastname: str
    birthdate: datetime


@surql_collection("books")
class Book(BaseModel):
    title: str
    pages: Optional[int]
    description: str
    weight: float
    writer: Writer

print(Metadata.collect())