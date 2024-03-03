from pydantic import BaseModel
from pydantic_surql import surql_collection
from .types.table import SurQLTable

class Person(BaseModel):
    firstname: str
    lastname: str
    age: int
    links: list[str]

@surql_collection("Library")
class Library(BaseModel):
    name: str
    location: str
    manager: Person

@surql_collection("Book")
class Book(BaseModel):
    title: str
    language: str
    price: float
    author: Person
    tags: list[str] | None
    bought_by: list[Person] | None
    libraries: list[Library] | None

def main():
    print("debuging pydantic_surql")
    print(SurQLTable(model=Library).sdl)
    print(SurQLTable(model=Book).sdl)
    print("debug done")