from datetime import datetime
from typing import Any, Optional
from pydantic_surql import toSurql, Mapper
from pydantic_surql.types import SurQLNullable
from pydantic import BaseModel, Field

@toSurql("basic_types")
class BasicTypesTest(BaseModel):
    """
        test all basic types parsing
    """
    t_str: str = Field(description="should be a string")
    t_float: float = Field(description="should be a number")
    t_int: int = Field(description="should be a number")
    t_bool: bool = Field(description="should be a boolean")
    t_date: datetime = Field(description="should be a datetime")
    t_nullable: str | SurQLNullable = Field(description="should be a nullable string")
    t_optional: Optional[str] = Field(description="should be an optional string")
    t_optional_nullable: Optional[str | SurQLNullable] = Field(description="should be an optional nullable string")
    t_any: Any = Field(description="should be an any type")
    t_dict: dict = Field(description="should be an object")
    t_multi: str | int | float | bool | datetime | dict = Field(description="should be a multi type")

@toSurql("basic_array_types")
class BasicArrayTypesTest(BaseModel):
    """
        test all basic array types parsing :
        string, number, datetime, bool
    """
    t_str: list[str]
    t_float: list[float]
    t_int: list[int]
    t_bool: list[bool]
    t_date: list[datetime]
    t_dict: list[dict]
    t_nullable: list[str | SurQLNullable]
    t_optional: Optional[list[str]]
    t_optional_nullable: Optional[list[str | SurQLNullable]]
    t_any: list[Any]
    t_multi: list[str | int | float | bool | datetime | dict]

def main():
    for table in Mapper.tables:
        print(table.model_dump_json(indent=4))